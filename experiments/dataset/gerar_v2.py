"""Gerador v2 do dataset do plano de testes: um exercício COMPLETO por chamada ao professor.

Uso:  python experiments/dataset/gerar_v2.py <modelo> <saida.jsonl> <quantidade> [semente] [threads] [chamadas_por_minuto]
Exemplo: python experiments/dataset/gerar_v2.py nvidia/nemotron-3-ultra-550b-a55b experiments/execucoes/piloto_v2.jsonl 10

O professor escreve o pedido, a solução, a spec (no formato do agente, sem os resultados escritos nela), o plano e os casos
de teste (só as entradas). O meu programa executa a solução para obter os valores esperados: eles nunca vêm do modelo.
Cada exercício aceito vira um exemplo de treino: o prompt do plano de testes do agente e o plano de testes certo.
"""
import json
import random
import re
import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(RAIZ / "src"))

import gerar_tarefas
from minicode.spec.diagnostico import normalizar_texto
from minicode.spec.documentos import validar_plano, validar_spec
from minicode.spec.plano_de_testes import criterios_da_spec, mensagens_plano_de_testes

SISTEMA = """Você cria exercícios de programação em Python para treinar e avaliar um agente de programação. Cada exercício traz tudo o que o agente produziria antes de escrever o código. Escreva tudo em português.

Responda SOMENTE com estes seis blocos, nesta ordem, cada um entre as suas tags:

<arquivo>o nome do arquivo, por exemplo frete.py</arquivo>
<pedido>um texto curto (1 a 3 frases), no estilo de um usuário: cita o arquivo e o nome da função ou classe e descreve TODOS os comportamentos, inclusive os casos inválidos (por exemplo, levanta ValueError)</pedido>
<referencia>o código Python correto, que cumpre exatamente o pedido</referencia>
<especificacao>
# Specification

## Objective
(uma frase)

## Acceptance Criteria
- (um critério verificável sobre o comportamento; descreva a REGRA e não escreva o resultado de uma chamada específica; no máximo um exemplo na spec toda)
- (de 3 a 6 critérios, um por linha começando com "-")
</especificacao>
<plano>
1. (de 3 a 6 passos numerados, um por linha)
</plano>
<casos>
[{"criterio": "(copie EXATAMENTE um critério da especificação, sem o hífen)", "entrada": "soma(2, 3)"}, {"criterio": "(outro critério)", "entrada": "soma(-1, 1)"}]
</casos>

No bloco casos, escreva uma lista JSON de 6 a 10 objetos: cada critério da especificação precisa de pelo menos um caso, e as entradas devem exercitar a regra e os limites. No máximo metade dos casos pode levantar exceção; os demais devem devolver valores comuns e diferentes entre si. A entrada é uma expressão Python que chama o código. NÃO escreva o resultado esperado.

Regras do exercício: só a biblioteca padrão, sem arquivos, rede, aleatoriedade nem data ou hora atuais. Para classes, escreva vários comandos separados por ponto e vírgula, terminando em uma expressão. Use só valores simples (números, textos, listas, dicionários, tuplas, booleanos, None). O resultado de cada entrada tem que ser sempre o mesmo: sem id() ou hash(), sem set impresso diretamente (use sorted) e sem objetos que mostram o endereço de memória."""

MIN_CRITERIOS = 3
MAX_FRACAO_QUE_A_SPEC_ENTREGA = 0.5


def bloco(texto, tag):
    achou = re.search(rf"<{tag}>(.*?)</{tag}>", texto, re.DOTALL)
    return achou.group(1).strip() if achou else None


def extrair_exercicio(texto):
    # os seis blocos da resposta, ou None se faltar algum ou se os casos não forem uma lista JSON
    campos = {tag: bloco(texto, tag) for tag in ("arquivo", "pedido", "referencia", "especificacao", "plano", "casos")}
    if any(valor is None for valor in campos.values()):
        return None
    codigo = re.sub(r"^```(?:python)?\s*\n|\n?```\s*$", "", campos["referencia"].strip())   # tira a cerca de código, se houver
    try:
        inicio, fim = campos["casos"].find("["), campos["casos"].rfind("]")
        casos = json.loads(campos["casos"][inicio:fim + 1])
    except json.JSONDecodeError:
        return None
    return {**campos, "referencia": codigo, "casos": casos}


def esperado_em_texto(saida):
    return saida["repr"] if saida["ok"] else saida["excecao"]


def palavras(texto):
    return set(re.findall(r"\w+", normalizar_texto(texto)))


def associar_criterio(texto, criterios):
    # o critério da spec que o caso cita: igual, ou o mais parecido (a partir de 60% das palavras)
    alvo = normalizar_texto(str(texto).lstrip("-* ").strip())
    for criterio in criterios:
        if normalizar_texto(criterio) == alvo:
            return criterio
    melhor, nota = None, 0.0
    for criterio in criterios:
        nota_do_criterio = len(palavras(alvo) & palavras(criterio)) / max(len(palavras(alvo) | palavras(criterio)), 1)
        if nota_do_criterio > nota:
            melhor, nota = criterio, nota_do_criterio
    return melhor if nota >= 0.6 else None


def validar_exercicio(bruto, existentes=()):
    # (registro, "") se o exercício serve; (None, motivo) se não
    if not isinstance(bruto, dict):
        return None, "resposta sem os blocos"
    try:
        arquivo, pedido, referencia = bruto["arquivo"], bruto["pedido"], bruto["referencia"]
        especificacao, plano, casos = bruto["especificacao"].strip(), bruto["plano"], bruto["casos"]
        if isinstance(plano, list):
            plano = "\n".join(str(p) for p in plano)
        assert all(isinstance(x, str) for x in (arquivo, pedido, referencia, plano)) and isinstance(casos, list)
    except (KeyError, TypeError, AssertionError, AttributeError):
        return None, "campos faltando ou com tipo errado"

    ok, motivo = validar_spec(especificacao)
    if not ok:
        return None, "spec inválida"
    criterios = criterios_da_spec(especificacao)
    if len(criterios) < MIN_CRITERIOS:
        return None, "poucos critérios"
    if not validar_plano(plano)[0]:
        return None, "plano inválido"

    mantidos = []
    for caso in casos:
        if not isinstance(caso, dict) or not isinstance(caso.get("entrada"), str) or not caso["entrada"].strip():
            continue
        criterio = associar_criterio(caso.get("criterio", ""), criterios)
        if criterio:
            mantidos.append({"criterio": criterio, "entrada": caso["entrada"].strip()})
    if {c["criterio"] for c in mantidos} != set(criterios):
        return None, "algum critério ficou sem caso"

    try:
        base = gerar_tarefas.normalizar({"arquivo": arquivo, "pedido": pedido, "referencia": referencia, "entradas": [c["entrada"] for c in mantidos]})
    except SyntaxError:
        return None, "referência com erro de sintaxe"
    saidas, motivo = gerar_tarefas.validar_tarefa(base, existentes)
    if saidas is None:
        return None, motivo

    texto_da_spec = normalizar_texto(especificacao)
    entregues = sum(1 for s in saidas if s["ok"] and len(s["repr"]) > 2 and normalizar_texto(s["repr"]) in texto_da_spec)
    if entregues > MAX_FRACAO_QUE_A_SPEC_ENTREGA * len(saidas):
        return None, "a spec entrega os resultados"

    prontos = [dict(c, esperado=esperado_em_texto(s)) for c, s in zip(mantidos, saidas)]
    return {**base, "especificacao": especificacao, "plano": plano.strip(), "casos": prontos}, ""


def exemplo_de_treino(registro):
    # o prompt do plano de testes do agente e a resposta certa, com os valores executados
    mensagens = mensagens_plano_de_testes(registro["pedido"], registro["especificacao"], registro["plano"])
    casos = [{"criterio": c["criterio"], "entrada": c["entrada"], "esperado": c["esperado"]} for c in registro["casos"]]
    return {"tarefa_id": registro["id"], "modelo": registro["modelo"], "mensagens": mensagens,
            "resposta": json.dumps({"casos": casos}, ensure_ascii=False)}


def pedir_exercicio(professor, rng, usados=()):
    tema, estilo, regras = rng.choice(gerar_tarefas.TEMAS), rng.choice(gerar_tarefas.ESTILOS), rng.choice([1, 2, 2, 3, 3, 4])
    proibidos = sorted(gerar_tarefas.nomes_do_benchmark() | set(rng.sample(list(usados), min(len(usados), 40))))   # os do benchmark e uma amostra dos já criados
    usuario = f"Tema: {tema}. Estilo: {estilo}. Regras distintas no comportamento: {regras}. Não use nenhum destes nomes de arquivo, função ou classe: {', '.join(proibidos)}."
    texto = professor([{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}], temperature=0.8, max_tokens=3500)
    return extrair_exercicio(texto), {"tema": tema, "estilo": estilo, "regras": regras}


def gerar(professor, saida, quantidade, semente=0, threads=3, log=print):
    saida = Path(saida)
    existentes = [json.loads(l) for l in saida.read_text(encoding="utf-8").splitlines() if l.strip()] if saida.is_file() else []
    rng = random.Random(semente + len(existentes))
    descartes, tentativas = {}, 0

    def uma(_):
        # pede e VALIDA dentro da thread: a validação executa a referência e é o que mais demora
        try:
            conhecidos = list(existentes)
            bruto, meta = pedir_exercicio(professor, rng, [e["nome"] for e in conhecidos])
            registro, motivo = validar_exercicio(bruto, conhecidos)
            return registro, motivo, meta
        except Exception as erro:
            return None, type(erro).__name__, {}

    def repete_um_do_mesmo_lote(registro):
        # as threads de um lote não se veem; confere de novo contra o que acabou de ser aceito
        return any(e["nome"] == registro["nome"] or gerar_tarefas.similaridade(registro["pedido"], e["pedido"]) > gerar_tarefas.MAX_SIMILARIDADE_ENTRE_SINTETICAS for e in existentes)

    enviadas, limite = 0, 6 * quantidade + 6   # trava: modelo fora do ar ou exigente demais
    with ThreadPoolExecutor(threads) as pool:
        pendentes = set()
        while True:
            # sempre `threads` pedidos em andamento: uma chamada lenta não segura as outras
            while len(pendentes) < threads and len(existentes) < quantidade and enviadas < limite:
                pendentes.add(pool.submit(uma, enviadas))
                enviadas += 1
            if not pendentes:
                break
            prontos, pendentes = wait(pendentes, return_when=FIRST_COMPLETED)
            for futuro in prontos:
                registro, motivo, meta = futuro.result()
                tentativas += 1
                if len(existentes) >= quantidade:
                    continue   # já chegou à meta; as respostas que ainda estavam a caminho são ignoradas
                if registro is not None and repete_um_do_mesmo_lote(registro):
                    registro, motivo = None, "repete uma tarefa sintética"
                if registro is None:
                    descartes[motivo] = descartes.get(motivo, 0) + 1
                    continue
                registro = {"id": f"v{len(existentes) + 1:04d}", "modelo": professor.modelo, **meta, **registro}
                with open(saida, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")
                existentes.append(registro)
                log(f"[{len(existentes)}/{quantidade}] {registro['nome']} ({meta['tema']}, {meta['regras']} regras, {len(registro['casos'])} casos) | tentativas {tentativas}")
    log(f"pronto: {len(existentes)} exercícios em {tentativas} tentativas; descartes: {descartes}")
    return existentes


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from professor import Professor
    modelo, saida, quantidade = sys.argv[1], sys.argv[2], int(sys.argv[3])
    semente = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    threads = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    por_minuto = int(sys.argv[6]) if len(sys.argv) > 6 else 30   # limite de chamadas por minuto deste processo
    professor = Professor(modelo, por_minuto=por_minuto, tempo=45, arquivo_de_uso=RAIZ / "experiments" / "execucoes" / "uso_tokens.jsonl")
    gerar(professor, saida, quantidade, semente, threads, log=lambda m: print(m, flush=True))


if __name__ == "__main__":
    main()

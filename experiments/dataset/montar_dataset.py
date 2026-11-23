"""Junta os exercícios gerados pelos professores e monta o dataset final do plano de testes.

Uso:  python experiments/dataset/montar_dataset.py <pasta_de_saida> <exercicios1.jsonl> [exercicios2.jsonl ...]

Passos: renumera os ids, tira exercícios repetidos entre os arquivos, divide POR EXERCÍCIO em treino/validação/teste
(sorteio com semente fixa, separado por professor para que cada divisão tenha os dois) e grava, para cada divisão:
  registros_<divisão>.jsonl  o exercício completo (com a referência, usada pelo oráculo na avaliação)
  exemplos_<divisão>.jsonl   o exemplo de treino: mensagens do agente + resposta certa
Também grava relatorio.md com os números do dataset. O teste real do trabalho são as 25 tarefas do benchmark; o teste daqui é um complemento.
"""
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))   # experiments/ (oraculo)
sys.path.insert(0, str(AQUI.parents[1] / "src"))

import gerar_tarefas
from gerar_v2 import esperado_em_texto, exemplo_de_treino
from minicode.spec.plano_de_testes import criterios_da_spec

FRACAO_TESTE = 0.1
FRACAO_VALIDACAO = 0.1


def ler(caminho):
    return [json.loads(l) for l in Path(caminho).read_text(encoding="utf-8").splitlines() if l.strip()]


def sem_repetidos(registros):
    # mantém o primeiro de cada par com o mesmo nome ou com pedidos muito parecidos
    mantidos, tirados = [], 0
    for r in registros:
        if any(m["nome"] == r["nome"] or gerar_tarefas.similaridade(m["pedido"], r["pedido"]) > gerar_tarefas.MAX_SIMILARIDADE_ENTRE_SINTETICAS for m in mantidos):
            tirados += 1
            continue
        mantidos.append(r)
    return mantidos, tirados


def caso_suspeito(caso):
    # casos cujo valor esperado não se deduz da spec: a entrada mexe num atributo privado (_x), ou o critério
    # começa com "Levanta ..." e o esperado é um valor
    if re.search(r"\._\w+", caso["entrada"]):
        return True
    comeca_com_erro = re.match(r"\W*(levant\w*|raises?|throws?)\b", caso["criterio"], re.I)
    return bool(comeca_com_erro) and not re.search(r"Error|Exception", caso["esperado"][:40])


PALAVRAS_EM_INGLES = re.compile(r"\b(raises?|returns?|the|when|if|must|should|is|are|handles?|accepts?)\b", re.I)
PALAVRAS_EM_PORTUGUES = re.compile(r"\b(retorna|levanta|quando|deve|para|com|se|não|uma|os|as)\b", re.I)


def criterios_em_ingles(registro):
    # a maior parte dos critérios da spec está escrita em inglês (o agente trabalha em português)
    criterios = criterios_da_spec(registro["especificacao"])
    em_ingles = sum(len(PALAVRAS_EM_INGLES.findall(c)) > len(PALAVRAS_EM_PORTUGUES.findall(c)) for c in criterios)
    return em_ingles > len(criterios) / 2


FALA_EM_ERRO = re.compile(r"levant|lan[cç]|raise|ValueError|TypeError|KeyError|IndexError|rejeit", re.I)
NEGA_O_ERRO = re.compile(r"n[ãa]o (levant|lan[cç])|sem (levant|lan[cç])|ignor", re.I)
FALA_EM_RETORNO = re.compile(r"retorn|devolv|return|resulta|produz|armazen|calcul|mant[eé]m|aceit", re.I)


def criterio_de_erro_sem_caso_de_erro(registro):
    # um critério que só diz "levanta erro", mas nenhum dos casos dele espera um erro: a solução de referência contradiz a spec
    for criterio in criterios_da_spec(registro["especificacao"]):
        if FALA_EM_ERRO.search(criterio) and not NEGA_O_ERRO.search(criterio) and not FALA_EM_RETORNO.search(criterio):
            casos = [c for c in registro["casos"] if c["criterio"] == criterio]
            if casos and not any(re.search(r"Error|Exception", c["esperado"][:40]) for c in casos):
                return True
    return False


# exercícios que li e cuja solução de referência contradiz a spec ou o pedido (decididos pela leitura, por arquivo)
EXCLUIDOS_POR_LEITURA = {
    "content_negotiation.py": "em empate de q a referência escolhe o tipo menos específico, contra a spec",
    "sequencia_variada.py": "um caso usa nomes de atributo (primeiro, segundo) que o pedido não define",
    "parametros_url.py": "a spec manda levantar ValueError para '?=valor', mas a referência devolve {'': 'valor'}",
}
FORMATO_MONETARIO_QUEBRADO = re.compile(r"R\$[^ \d-]|R\$ ?,|R\$ 0\d|'0\d{2}\.\d{3}")


def excluido_por_leitura(registro):
    # na lista de exclusões manuais, ou com o formato monetário quebrado nos valores esperados (zeros à esquerda, "R$," sem espaço)
    return registro.get("arquivo") in EXCLUIDOS_POR_LEITURA or any(FORMATO_MONETARIO_QUEBRADO.search(c["esperado"]) for c in registro["casos"])


TRADUCOES = AQUI.parent / "execucoes" / "traducoes.json"   # fica na pasta ignorada pelo git (arquivo de trabalho)


def aplicar_traducoes(registros):
    # passa para português a spec dos exercícios que vieram em inglês, por nome do exercício e na ordem dos critérios;
    # os valores esperados não mudam (vêm da execução da referência). Devolve (registros, quantos foram traduzidos)
    if not TRADUCOES.is_file():
        return registros, 0
    traducoes = json.loads(TRADUCOES.read_text(encoding="utf-8"))
    resultado, feitos = [], 0
    for r in registros:
        t = traducoes.get(r["nome"])
        antigos = criterios_da_spec(r["especificacao"])
        if t and criterios_em_ingles(r) and len(t["criterios"]) == len(antigos):
            mapa = dict(zip(antigos, t["criterios"]))
            spec = "# Specification\n\n## Objective\n" + t["objetivo"] + "\n\n## Acceptance Criteria\n" + "\n".join(f"- {c}" for c in t["criterios"])
            r = {**r, "especificacao": spec, "casos": [{**c, "criterio": mapa.get(c["criterio"], c["criterio"])} for c in r["casos"]]}
            feitos += 1
        resultado.append(r)
    return resultado, feitos


CORRECOES_DE_REFERENCIA = AQUI.parent / "execucoes" / "correcoes_referencia.json"   # {arquivo: [[trecho_errado, trecho_certo], ...]}


def aplicar_correcoes_de_referencia(registros):
    # conserta a solução de referência de alguns exercícios (defeitos que li) e executa as entradas de novo: os valores esperados
    # continuam vindo da execução. Devolve (registros, quantos foram corrigidos)
    if not CORRECOES_DE_REFERENCIA.is_file():
        return registros, 0
    correcoes = json.loads(CORRECOES_DE_REFERENCIA.read_text(encoding="utf-8"))
    resultado, feitos = [], 0
    for r in registros:
        trechos = correcoes.get(r.get("arquivo"))
        if trechos and all(errado in r["referencia"] for errado, _ in trechos):
            referencia = r["referencia"]
            for errado, certo in trechos:
                referencia = referencia.replace(errado, certo)
            saidas, _ = gerar_tarefas.saidas_da_referencia({"arquivo": r["arquivo"], "referencia": referencia, "entradas": [c["entrada"] for c in r["casos"]]})
            if saidas is not None:
                r = {**r, "referencia": referencia, "casos": [{**c, "esperado": esperado_em_texto(s)} for c, s in zip(r["casos"], saidas)]}
                feitos += 1
        resultado.append(r)
    return resultado, feitos


def sem_casos_repetidos(casos):
    # o mesmo critério com a mesma entrada duas vezes: fica o primeiro
    vistos, unicos = set(), []
    for c in casos:
        if (c["criterio"], c["entrada"]) not in vistos:
            vistos.add((c["criterio"], c["entrada"]))
            unicos.append(c)
    return unicos


def filtrar_casos(registros):
    # tira os casos suspeitos e os repetidos; o exercício que ficar com algum critério sem caso, ou com critérios em inglês, sai do dataset
    mantidos, casos_tirados, exercicios_tirados = [], 0, 0
    for r in registros:
        if criterios_em_ingles(r) or excluido_por_leitura(r):
            exercicios_tirados += 1
            continue
        casos = [c for c in sem_casos_repetidos(r["casos"]) if not caso_suspeito(c)]
        if {c["criterio"] for c in casos} != set(criterios_da_spec(r["especificacao"])):
            exercicios_tirados += 1
            continue
        if criterio_de_erro_sem_caso_de_erro({**r, "casos": casos}):
            exercicios_tirados += 1
            continue
        casos_tirados += len(r["casos"]) - len(casos)
        mantidos.append({**r, "casos": casos})
    return mantidos, casos_tirados, exercicios_tirados


TESTE_CONGELADO = AQUI / "teste_congelado.json"


def dividir(registros, semente=0):
    # sorteio por exercício, separado por professor: devolve {"treino": [...], "validacao": [...], "teste": [...]}
    # o teste vem congelado (os exercícios que li à mão), se o arquivo existir; a validação e o treino vêm do sorteio do resto
    congelados = set(json.loads(TESTE_CONGELADO.read_text(encoding="utf-8"))["nomes"]) if TESTE_CONGELADO.is_file() else set()
    if not any(r["nome"] in congelados for r in registros):
        congelados = set()   # nenhum exercício da lista nesta montagem (por exemplo, nos testes): sorteia o teste também
    rng = random.Random(semente)
    partes = {"treino": [], "validacao": [], "teste": [r for r in registros if r["nome"] in congelados]}
    for modelo in sorted({r["modelo"] for r in registros}):
        grupo = [r for r in registros if r["modelo"] == modelo and r["nome"] not in congelados]
        rng.shuffle(grupo)
        n_teste = 0 if congelados else round(len(grupo) * FRACAO_TESTE)
        n_validacao = round(len(grupo) * FRACAO_VALIDACAO)
        partes["teste"] += grupo[:n_teste]
        partes["validacao"] += grupo[n_teste:n_teste + n_validacao]
        partes["treino"] += grupo[n_teste + n_validacao:]
    return partes


LIMIAR_DE_PARECIDOS = 0.4
PALAVRAS_SEM_INFORMACAO = set("a o as os de da do das dos em no na nos nas e que um uma para com se por ao é ser py arquivo função funções classe método implemente crie levanta valueerror typeerror retorna deve".split())


def palavras_do_exercicio(registro):
    texto = registro["pedido"] + " " + registro["nome"].replace("_", " ")
    return {p for p in re.findall(r"[a-zà-ú]{3,}", texto.lower()) if p not in PALAVRAS_SEM_INFORMACAO}


def parecido_com_algum(registro, grupo):
    a = palavras_do_exercicio(registro)
    return any(len(a & b) / max(len(a | b), 1) >= LIMIAR_DE_PARECIDOS for b in (palavras_do_exercicio(g) for g in grupo))


def afastar_parecidos(partes):
    # exercício de validação ou de teste parecido com algum do treino vai para o treino: o teste sintético fica mais independente
    movidos = 0
    for nome in ("validacao", "teste"):
        ficam = []
        for r in partes[nome]:
            if parecido_com_algum(r, partes["treino"]):
                partes["treino"].append(r)
                movidos += 1
            else:
                ficam.append(r)
        partes[nome] = ficam
    return partes, movidos


def relatorio(partes, tirados, total_lido, filtro=(0, 0)):
    linhas = ["# Dataset do plano de testes\n", f"Exercícios lidos: {total_lido}. Tirados por repetição: {tirados}. "
              f"Filtro de casos suspeitos: {filtro[0]} casos removidos e {filtro[1]} exercícios removidos (ficaram com algum critério sem caso).\n",
              "| Divisão | Exercícios | Casos | Casos de exceção |\n|---|---|---|---|"]
    for nome, regs in partes.items():
        casos = [c for r in regs for c in r["casos"]]
        excecoes = sum(1 for c in casos if "Error" in c["esperado"] or "Exception" in c["esperado"])
        linhas.append(f"| {nome} | {len(regs)} | {len(casos)} | {excecoes} ({100 * excecoes / max(len(casos), 1):.0f}%) |")
    todos = [r for regs in partes.values() for r in regs]
    for titulo, chave in (("Professor", "modelo"), ("Estilo", "estilo"), ("Regras distintas", "regras")):
        linhas.append(f"\n## {titulo}\n\n| Valor | Exercícios |\n|---|---|")
        linhas += [f"| {valor} | {n} |" for valor, n in Counter(r.get(chave) for r in todos).most_common()]
    linhas.append("\n## Temas\n\n| Tema | Exercícios |\n|---|---|")
    linhas += [f"| {valor} | {n} |" for valor, n in Counter(r.get("tema") for r in todos).most_common()]
    casos_por = [len(r["casos"]) for r in todos]
    linhas.append(f"\nCasos por exercício: mínimo {min(casos_por)}, média {sum(casos_por) / len(casos_por):.1f}, máximo {max(casos_por)}.")
    return "\n".join(linhas) + "\n"


def montar(arquivos, saida, semente=0):
    registros = [r for arquivo in arquivos for r in ler(arquivo)]
    registros, traduzidos = aplicar_traducoes(registros)
    registros, corrigidos = aplicar_correcoes_de_referencia(registros)
    print(f"exercícios traduzidos do inglês: {traduzidos} | referências corrigidas: {corrigidos}")
    unicos, tirados = sem_repetidos(registros)
    unicos, casos_tirados, exercicios_tirados = filtrar_casos(unicos)
    for numero, r in enumerate(unicos, start=1):
        r["id"] = f"e{numero:04d}"
    partes, movidos = afastar_parecidos(dividir(unicos, semente))
    print(f"movidos para o treino por serem parecidos com um exercício do treino: {movidos}")
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    for nome, regs in partes.items():
        with open(saida / f"registros_{nome}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in regs)
        with open(saida / f"exemplos_{nome}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(exemplo_de_treino(r), ensure_ascii=False) + "\n" for r in regs)
    (saida / "relatorio.md").write_text(relatorio(partes, tirados, len(registros), (casos_tirados, exercicios_tirados)), encoding="utf-8")
    return partes, tirados, (casos_tirados, exercicios_tirados)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    partes, tirados, filtro = montar(sys.argv[2:], sys.argv[1])
    print({nome: len(regs) for nome, regs in partes.items()}, "repetidos tirados:", tirados, "| filtro (casos, exercícios):", filtro)


if __name__ == "__main__":
    main()

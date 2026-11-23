"""Gerador v3 (piloto): lotes de exercícios para o plano de testes, com as regras aprendidas na revisão do dataset v2.

Uso:  python experiments/dataset/gerar_v3.py <modelo_gerador|qwen> <modelo_solucionador> <saida.jsonl> <quantidade> [semente] [threads]
Exemplo: python experiments/dataset/gerar_v3.py nvidia/nemotron-3.5-super-vl-120b-a12b nvidia/nemotron-3-ultra-550b-a55b experiments/execucoes/piloto_v3/lote1.jsonl 10

Em cima do gerar_v2 (um exercício por chamada, com threads), muda quatro coisas:
  1. o prompt do professor traz as regras de qualidade (nada de critério de implementação, mensagem, ordem ou fórmula
     que o pedido não defina; tudo em português; sem os temas em que o professor errou várias vezes);
  2. o tema é sorteado com peso inverso ao uso no dataset atual, e a lista de nomes proibidos vem do dataset inteiro;
  3. filtros extras: critério de implementação, texto em inglês, sleep, repr de objeto;
  4. SEGUNDO SOLUCIONADOR: outro modelo resolve o exercício só pelo pedido e pela spec; o código dele roda nas mesmas
     entradas e as divergências com a referência ficam em "solucionador" (é isso que pega referência errada).
O esperado continua vindo da execução da referência, nunca de um modelo.
"""
import json
import random
import re
import sys
import threading
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py
sys.path.insert(0, str(RAIZ / "src"))

import gerar_tarefas
import gerar_v2
import oraculo
from temas_v4 import TEMAS_V4 as _V4

# os temas novos: os de temas_v4.py mais os de temas_v5.json
TEMAS_V4 = list(_V4) + [t for t in json.loads((AQUI / 'temas_v5.json').read_text(encoding='utf-8'))]

# o dataset já existente (registros_*.jsonl), usado para não repetir nomes e para contar o uso dos temas
DATASET_ATUAL = RAIZ / "experiments" / "execucoes" / "dataset_v2"

REGRAS_EXTRAS = """

REGRAS DE QUALIDADE (muito importantes; exercícios que as violam são descartados):
- Cada critério descreve um comportamento que se observa pela entrada e pela saída. NUNCA escreva critério sobre a implementação ("usa X internamente", "não usa bibliotecas", "reutiliza a função Y", "é determinístico", "mantém estado interno").
- Os casos só podem exigir o que o pedido e a spec definem. Não exija mensagem de erro (só o tipo da exceção), nem uma ordem de resultados que o pedido não define, nem fórmula, tabela ou constante que o pedido não traga (se usar constantes, escreva-as no pedido), nem arredondamento que dependa de empate exato (como 0.125 para 2 casas).
- Se o pedido ou um critério trouxer um exemplo numérico, ele tem de coincidir com o que a referência devolve.
- O PEDIDO tem de nomear tudo o que os casos usam: cada função, classe, método e atributo (com os parâmetros), as chaves de qualquer dicionário devolvido, o que um método devolve (valor, lista de tuplas, dicionário...), os parâmetros opcionais e seus valores padrão, e qualquer constante ou tabela de valores (por exemplo "bull vale 25"). Se um caso lê um atributo ou chama um método, o nome dele tem de estar escrito no pedido.
- Todo o texto (pedido, spec e plano) em português. Cada passo do plano em português.
- Não crie exercícios de: datas e dia da semana, dígito verificador (Luhn, CPF, CNPJ), signos, notas musicais, conversão de bases numéricas, MIME, CSV."""

# o prompt do v2 mais as regras de qualidade aprendidas na revisão
SISTEMA = gerar_v2.SISTEMA + REGRAS_EXTRAS

# expressões regulares dos filtros extras
# - IMPLEMENTACAO: palavras de um critério que fala da implementação em vez do comportamento
# - INGLES / PORTUGUES: palavras comuns de cada língua, para detectar texto em inglês
IMPLEMENTACAO = re.compile(
    r"\b(internamente|biblioteca|reutiliza|determin[ií]stic|usa (a )?fun[cç][aã]o|n[aã]o utiliza"
    r"|sem usar|estado interno|complexidade|in-place)\b",
    re.I,
)
INGLES = re.compile(r"\b(the|and|with|for|to|of|is|if|that|each|when|in)\b", re.I)
PORTUGUES = re.compile(r"\b(o|a|de|para|com|que|se|um|uma|e|do|da|em|os|as)\b", re.I)


# todos os registros já existentes (treino, validação e teste)
def dataset_atual():
    registros = []
    for conjunto in ("treino", "validacao", "teste"):
        arquivo = DATASET_ATUAL / f"registros_{conjunto}.jsonl"
        if arquivo.is_file():
            registros += [json.loads(l) for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()]
    return registros


# nomes de arquivo e de definições (def/class) das referências, para não repetir nenhum
def nomes_do_dataset(registros):
    nomes = set()
    for r in registros:
        nomes.add(Path(r["arquivo"]).stem)
        nomes.update(re.findall(r"^(?:def|class) (\w+)", r["referencia"], re.M))
    return nomes


# Controle de temas sem reposição: os já usados em lotes anteriores ficam em temas_usados.json e os sorteados
# nesta execução ficam em _SORTEADOS (a trava impede duas threads de sortear o mesmo tema).
ARQUIVO_TEMAS = AQUI / "temas_usados.json"
_TRAVA = threading.Lock()
_SORTEADOS = set()


def temas_usados():
    return set(json.loads(ARQUIVO_TEMAS.read_text(encoding="utf-8"))) if ARQUIVO_TEMAS.exists() else set()


# acrescenta os temas deste lote ao arquivo de temas usados
def registrar_temas(registros):
    novos = temas_usados() | {r["tema"] for r in registros}
    ARQUIVO_TEMAS.write_text(json.dumps(sorted(novos), ensure_ascii=False, indent=1), encoding="utf-8")


def pedir_exercicio(professor, rng, usados=()):
    conhecidos = dataset_atual()
    uso = {}
    for r in conhecidos:
        uso[r.get("tema")] = uso.get(r.get("tema"), 0) + 1
    with _TRAVA:
        # sem reposição: fora os temas de lotes anteriores (temas_usados.json) e os já sorteados nesta execução
        temas = [t for t in TEMAS_V4 if t not in temas_usados() and t not in _SORTEADOS]
        if not temas:
            raise RuntimeError("acabaram os temas novos")
        tema = rng.choice(temas)
        _SORTEADOS.add(tema)
    estilo, regras = rng.choice(gerar_tarefas.ESTILOS), rng.choice([1, 2, 2, 3, 3, 4])
    # nomes proibidos: os do benchmark, uma amostra de 80 do dataset e os já criados neste lote
    proibidos = sorted(
        gerar_tarefas.nomes_do_benchmark()
        | set(rng.sample(sorted(nomes_do_dataset(conhecidos)), 80))
        | set(usados)
    )
    usuario = (
        f"Tema: {tema}. Estilo: {estilo}. Regras distintas no comportamento: {regras}. "
        f"Não use nenhum destes nomes de arquivo, função ou classe: {', '.join(proibidos)}."
    )
    texto = professor(
        [{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}],
        temperature=0.8,
        max_tokens=4500,
    )
    return gerar_v2.extrair_exercicio(texto), {"tema": tema, "estilo": estilo, "regras": regras}


TEMAS_PROIBIDOS = re.compile(
    r"cpf|cnpj|data|hor[aá]rio|dia da semana|semana|signo|nota musical|notas e frequ|frequ[eê]ncia"
    r"|base num|luhn|d[ií]gito verificador|mime|csv|resum",
    re.I,
)
_NOMES_DO_DATASET = None


# os nomes do dataset atual (sem os que começam com "_"), calculados só uma vez
def nomes_ja_usados():
    global _NOMES_DO_DATASET
    if _NOMES_DO_DATASET is None:
        _NOMES_DO_DATASET = {n for n in nomes_do_dataset(dataset_atual()) if not n.startswith("_")}
    return _NOMES_DO_DATASET


def filtro_extra(registro):
    # (registro, "") ou (None, motivo)

    # nomes de função e classe (públicos) que a referência define; não podem repetir os do dataset
    definidos = {
        n for n in re.findall(r"^(?:def|class) (\w+)", registro["referencia"], re.M)
        if not n.startswith("_")
    }
    repetidos = definidos & nomes_ja_usados()
    if repetidos or Path(registro["arquivo"]).stem in nomes_ja_usados():
        return None, f"nome já usado no dataset ({', '.join(sorted(repetidos))})"
    if any(re.search(r"\._\w+", c["entrada"]) for c in registro["casos"]):
        return None, "o caso acessa atributo privado"
    # todo método, atributo e função usados nos casos têm de estar nomeados no PEDIDO
    # métodos e funções da biblioteca padrão que não precisam estar no pedido
    comuns = {
        "append", "pop", "items", "keys", "values", "join", "sort", "upper", "lower", "split", "strip", "count",
        "index", "extend", "copy", "add", "remove", "update", "insert", "get", "format", "isalnum", "isdigit",
        "real", "imag", "pi", "sqrt",
    }
    nomes = set()
    for c in registro["casos"]:
        # tira os textos entre aspas antes de procurar nomes, para não confundir com o conteúdo de strings
        limpa = re.sub(r"'[^']*'|\"[^\"]*\"", "", c["entrada"])
        nomes |= set(re.findall(r"\.(\w+)", limpa)) | {n for n in re.findall(r"(\w+)\(", limpa) if n in definidos}
    faltam = sorted(
        n for n in nomes
        if n not in registro["pedido"] and n not in comuns and not n.startswith("_") and not n.isdigit()
    )
    if faltam:
        return None, f"o pedido não nomeia: {', '.join(faltam[:4])}"

    # critérios sobre a implementação (em vez do comportamento) são descartados
    criterios = gerar_v2.criterios_da_spec(registro["especificacao"])
    if any(IMPLEMENTACAO.search(c) for c in criterios):
        return None, "critério de implementação"

    # texto em inglês: muitas palavras inglesas comuns e mais do que metade das portuguesas
    for campo in ("especificacao", "plano", "pedido"):
        texto = registro[campo]
        if len(INGLES.findall(texto)) >= 6 and len(INGLES.findall(texto)) > 0.5 * len(PORTUGUES.findall(texto)):
            return None, "texto em inglês"
    # casos com sleep (lento), repr de objeto (o endereço de memória muda) ou esperado enorme
    for c in registro["casos"]:
        if "sleep" in c["entrada"] or "object at 0x" in c["esperado"]:
            return None, "sleep ou repr de objeto"
        if len(c["esperado"]) > 600:
            return None, "esperado muito longo"
    return registro, ""


# guarda a validação do v2 e acrescenta os filtros extras do v3 por cima dela
_validar_v2 = gerar_v2.validar_exercicio


def validar_exercicio(bruto, existentes=()):
    registro, motivo = _validar_v2(bruto, existentes)
    if registro is None:
        return None, motivo
    return filtro_extra(registro)


def segundo_solucionador(solucionador, registro):
    # outro modelo resolve só pelo pedido e pela spec; roda o código dele nas mesmas entradas e compara com a referência
    mensagens = [
        {"role": "system", "content": "Você é um programador Python. Implemente o que o pedido e a especificação descrevem. Só a biblioteca padrão. Responda SOMENTE com o código do arquivo, sem explicações."},
        {"role": "user", "content": f"Arquivo: {registro['arquivo']}\n\nPedido:\n{registro['pedido']}\n\nEspecificação:\n{registro['especificacao']}"}]
    try:
        codigo = solucionador(mensagens, temperature=0.2, max_tokens=3500)
    except Exception as erro:
        return {"situacao": "sem_resposta", "erro": type(erro).__name__}
    codigo = re.sub(r"^```(?:python)?\s*\n|\n?```\s*$", "", codigo.strip())
    try:
        compile(codigo, registro["arquivo"], "exec")
    except SyntaxError:
        return {"situacao": "codigo_invalido"}

    # roda o código do solucionador nas mesmas entradas dos casos
    saidas, motivo = gerar_tarefas.saidas_da_referencia({
        "arquivo": registro["arquivo"],
        "referencia": codigo,
        "entradas": [c["entrada"] for c in registro["casos"]],
    })
    if saidas is None:
        return {"situacao": "nao_executa", "motivo": motivo}

    # cada divergência com o esperado da referência é um sinal de referência errada ou de pedido ambíguo
    divergencias = []
    for caso, saida in zip(registro["casos"], saidas):
        veredito = oraculo.comparar(saida, caso["esperado"])
        if veredito == "errado":
            divergencias.append({
                "entrada": caso["entrada"][:160],
                "referencia": caso["esperado"][:80],
                "solucionador": (saida["repr"] if saida["ok"] else saida["excecao"])[:80],
            })
    return {
        "situacao": "ok" if not divergencias else "diverge",
        "casos": len(registro["casos"]),
        "divergencias": divergencias,
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from professor import Professor
    gerador, resolvedor, saida, quantidade = sys.argv[1], sys.argv[2], Path(sys.argv[3]), int(sys.argv[4])
    semente = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    threads = int(sys.argv[6]) if len(sys.argv) > 6 else 5
    pular_solucionador = len(sys.argv) > 7 and sys.argv[7] == "sem_solucionador"
    uso = RAIZ / "experiments" / "execucoes" / "uso_tokens.jsonl"
    if gerador.lower() == "qwen":
        # provedor Qwen cloud (compatível com a API da OpenAI): base, chave e modelo vêm do .env; a chave nunca é impressa
        import os
        from dotenv import load_dotenv
        load_dotenv(RAIZ / ".env", override=True)
        professor = Professor(
            os.environ["QWEN_MODEL"],
            por_minuto=20,
            tempo=120,
            arquivo_de_uso=uso,
            base=os.environ["QWEN_ENDPOINT"],
            chave=os.environ["QWEN_KEY"],
        )
    else:
        professor = Professor(gerador, por_minuto=30, tempo=90, arquivo_de_uso=uso)
    solucionador = Professor(resolvedor, por_minuto=30, tempo=90, arquivo_de_uso=uso)
    saida.parent.mkdir(parents=True, exist_ok=True)

    # troca a validação e o pedido do v2 pelos do v3 e reaproveita o laço de geração do v2
    gerar_v2.validar_exercicio = validar_exercicio
    gerar_v2.pedir_exercicio = pedir_exercicio
    registros = gerar_v2.gerar(professor, saida, quantidade, semente, threads, log=lambda m: print(m, flush=True))

    # depois da geração, o segundo solucionador confere cada exercício novo
    atualizados = []
    for r in registros:
        if "solucionador" not in r and not pular_solucionador:
            r["solucionador"] = segundo_solucionador(solucionador, r)
            print(f"  segundo solucionador {r['id']} {r['nome']}: {r['solucionador']['situacao']}", flush=True)
        atualizados.append(r)
    saida.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in atualizados), encoding="utf-8")
    registrar_temas(atualizados)


if __name__ == "__main__":
    main()

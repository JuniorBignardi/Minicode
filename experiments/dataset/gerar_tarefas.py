"""Gera tarefas sintéticas de programação para o dataset da Parte 2, verificadas por execução.

Uso:  python experiments/dataset/gerar_tarefas.py <saida.jsonl> <quantidade> [semente] [threads]

O 14B cria um exercício (pedido, solução de referência e entradas de exemplo). O programa só aceita o
exercício se a referência executar, for determinística e der saídas variadas. Os valores de saída vêm da
EXECUÇÃO da referência, nunca do modelo. Tarefas parecidas com as 25 do benchmark são descartadas,
porque elas são o conjunto de teste.
Precisa das variáveis MINICODE_API_BASE, MINICODE_API_KEY e MINICODE_MODEL.
"""
import ast
import json
import random
import re
import shutil
import sys
import tempfile
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI))

import oraculo

warnings.filterwarnings("ignore")   # a referência do modelo às vezes tem escapes inválidos em textos

from temas import TEMAS  # noqa: E402

ESTILOS = ["uma função", "duas funções que se complementam", "uma classe com estado", "uma função que levanta exceção em casos inválidos"]

SISTEMA = """Você cria pequenos exercícios de programação em Python para avaliar um agente de programação.

Regras do exercício:
- Só biblioteca padrão, sem entrada/saída de arquivos, sem rede, sem aleatoriedade, sem data ou hora atuais.
- O pedido é um texto curto em português (1 a 3 frases), no estilo de um usuário. Ele DEVE conter o nome do arquivo, o nome da função
  ou classe e TODOS os comportamentos, inclusive o que deve acontecer nos casos inválidos (por exemplo, "levanta ValueError").
  Exemplo do estilo: "Crie em notas.py a função media_ponderada(valores, pesos) que ..." 
- A referência é o código Python correto que cumpre exatamente o pedido, no arquivo indicado.
- As entradas são 8 a 12 expressões Python que CHAMAM o código. Para classes, vários comandos separados por ponto e vírgula, e o último
  comando é a expressão cujo valor será conferido. NÃO escreva o resultado esperado dentro da entrada. Elas devem exercitar cada regra
  do pedido e os casos de borda, e dar resultados diferentes entre si.
- Use apenas valores simples (números, textos, listas, dicionários, tuplas, booleanos, None).

Responda somente com o JSON pedido."""

ESQUEMA = {
    "type": "object",
    "properties": {
        "nome": {"type": "string"},
        "arquivo": {"type": "string"},
        "pedido": {"type": "string"},
        "referencia": {"type": "string"},
        "entradas": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["nome", "arquivo", "pedido", "referencia", "entradas"],
    "additionalProperties": False,
}

MAX_SIMILARIDADE = 0.45     # com o pedido de uma tarefa do benchmark
MAX_SIMILARIDADE_ENTRE_SINTETICAS = 0.6
MAX_FRACAO_DE_EXCECOES = 0.5


def palavras(texto):
    return set(re.findall(r"\w+", texto.lower()))


def similaridade(a, b):
    a, b = palavras(a), palavras(b)
    return len(a & b) / max(len(a | b), 1)


def pedidos_do_benchmark():
    return [t["tarefa"] for t in oraculo.tarefas_faceis.TAREFAS + oraculo.tarefas_dificeis.TAREFAS]


def nomes_do_benchmark():
    # nomes de arquivos e de definições das referências do benchmark, para não repetir nenhuma
    nomes = set()
    for referencias in (oraculo.REFERENCIAS_FACEIS, oraculo.REFERENCIAS_DIFICEIS):
        for arquivos in referencias.values():
            for caminho, codigo in arquivos.items():
                nomes.add(Path(caminho).stem)
                nomes.update(re.findall(r"^(?:def|class) (\w+)", codigo, re.M))
    return nomes


def saidas_da_referencia(tarefa):
    # executa as entradas na referência duas vezes. Devolve (saídas, motivo): saídas é None se a tarefa não serve.
    pasta = Path(tempfile.mkdtemp())
    try:
        (pasta / tarefa["arquivo"]).write_text(tarefa["referencia"], encoding="utf-8")
        rodadas = [[oraculo.executar_entrada(pasta, e) for e in tarefa["entradas"]] for _ in range(2)]
    finally:
        shutil.rmtree(pasta, ignore_errors=True)

    if rodadas[0] != rodadas[1]:
        return None, "não determinística"
    for saida in rodadas[0]:
        if not saida["ok"] and saida["excecao"] in oraculo.NAO_AVALIAVEIS:
            return None, f"a entrada não executa ({saida['excecao']})"
    return rodadas[0], ""


def validar_tarefa(tarefa, existentes=()):
    # (saídas, "") se a tarefa serve, ou (None, motivo)
    try:
        nome, arquivo = tarefa["nome"], tarefa["arquivo"]
        entradas = tarefa["entradas"]
        if not (isinstance(nome, str) and nome.isidentifier()):
            return None, "nome inválido"
        if not re.fullmatch(r"[a-z][a-z0-9_]*\.py", arquivo) or arquivo.startswith("test"):
            return None, "arquivo inválido"
        if not (5 <= len(entradas) <= 20) or not all(isinstance(e, str) and e.strip() for e in entradas):
            return None, "número de entradas inválido"
        compile(tarefa["referencia"], arquivo, "exec")
        if not tarefa["pedido"].strip() or arquivo not in tarefa["pedido"]:
            return None, "o pedido não cita o arquivo"
    except (KeyError, TypeError, SyntaxError) as erro:
        return None, f"estrutura inválida ({type(erro).__name__})"

    definidos = re.findall(r"^(?:def|class) (\w+)", tarefa["referencia"], re.M)
    if not definidos or not all(any(nome_definido in e for nome_definido in definidos) for e in entradas):
        return None, "alguma entrada não chama o código"
    if any(similaridade(tarefa["pedido"], p) > MAX_SIMILARIDADE for p in pedidos_do_benchmark()):
        return None, "parecida com uma tarefa do benchmark"
    if {nome, Path(arquivo).stem} & nomes_do_benchmark():
        return None, "nome igual ao de uma tarefa do benchmark"
    if any(e["nome"] == nome or similaridade(tarefa["pedido"], e["pedido"]) > MAX_SIMILARIDADE_ENTRE_SINTETICAS for e in existentes):
        return None, "repete uma tarefa sintética"

    saidas, motivo = saidas_da_referencia(tarefa)
    if saidas is None:
        return None, motivo
    comuns = [s for s in saidas if s["ok"]]
    if len(comuns) < 3 or len(saidas) - len(comuns) > MAX_FRACAO_DE_EXCECOES * len(saidas):
        return None, "poucas saídas comuns ou exceções demais"
    if len({s["repr"] for s in comuns}) < 3:
        return None, "saídas pouco variadas"
    return saidas, ""


def normalizar(tarefa):
    # Arruma o que o modelo costuma errar na forma, sem mexer no que importa (o código e os comportamentos):
    # o nome vem da primeira definição da referência e o pedido passa a citar o arquivo.
    arquivo = str(tarefa["arquivo"]).strip().lower().replace(" ", "_")
    arquivo = arquivo if arquivo.endswith(".py") else arquivo + ".py"
    definicoes = [n.name for n in ast.parse(tarefa["referencia"]).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    pedido = str(tarefa["pedido"]).strip()
    return {"nome": definicoes[0] if definicoes else "", "arquivo": arquivo,
            "pedido": pedido if arquivo in pedido else f"No arquivo {arquivo}: {pedido}",
            "referencia": tarefa["referencia"],
            "entradas": [e.strip() for e in tarefa["entradas"] if isinstance(e, str) and e.strip()]}


def pedir_tarefa(chat, formato_da_resposta, rng):
    tema, estilo, regras = rng.choice(TEMAS), rng.choice(ESTILOS), rng.choice([1, 2, 2, 3, 3, 4])
    usuario = f"Tema: {tema}. Estilo: {estilo}. Regras distintas no comportamento: {regras}."
    resposta = chat([{"role": "system", "content": SISTEMA}, {"role": "user", "content": usuario}],
                    temperature=0.9, response_format=formato_da_resposta(ESQUEMA, "tarefa"))
    return normalizar(json.loads(resposta)), {"tema": tema, "estilo": estilo, "regras": regras}


def gerar(chat, formato_da_resposta, saida, quantidade, semente=0, threads=2, log=print):
    saida = Path(saida)
    existentes = [json.loads(l) for l in saida.read_text(encoding="utf-8").splitlines() if l.strip()] if saida.is_file() else []
    rng = random.Random(semente + len(existentes))
    descartes, tentativas = {}, 0

    def uma_tentativa(_):
        try:
            return pedir_tarefa(chat, formato_da_resposta, rng)
        except Exception as erro:
            return None, {"erro": f"{type(erro).__name__}"}

    with ThreadPoolExecutor(threads) as pool:
        while len(existentes) < quantidade and tentativas < 10 * quantidade + 10:   # trava: modelo fora do ar ou exigente demais
            for tarefa, meta in pool.map(uma_tentativa, range(threads)):
                tentativas += 1
                if tentativas % 10 == 0:
                    log(f"  {tentativas} tentativas, {len(existentes)} aceitas; descartes até aqui: {descartes}")
                if tarefa is None:
                    descartes[meta["erro"]] = descartes.get(meta["erro"], 0) + 1
                    continue
                saidas, motivo = validar_tarefa(tarefa, existentes)
                if saidas is None:
                    descartes[motivo] = descartes.get(motivo, 0) + 1
                    continue
                registro = {"id": f"s{len(existentes) + 1:04d}", **meta, **tarefa, "saidas": saidas}
                with open(saida, "a", encoding="utf-8") as f:
                    f.write(json.dumps(registro, ensure_ascii=False) + "\n")
                existentes.append(registro)
                log(f"[{len(existentes)}/{quantidade}] {tarefa['nome']} ({meta['tema']}, {meta['regras']} regras) | tentativas {tentativas}")
                if len(existentes) >= quantidade:
                    break
    log(f"pronto: {len(existentes)} tarefas em {tentativas} tentativas; descartes: {descartes}")
    return existentes


def main():
    sys.path.insert(0, str(AQUI.parent.parent / "src"))
    from minicode.llm.client import chat
    from minicode.llm.esquema import formato_da_resposta
    saida, quantidade = sys.argv[1], int(sys.argv[2])
    semente = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    gerar(chat, formato_da_resposta, saida, quantidade, semente, threads, log=lambda m: print(m, flush=True))


if __name__ == "__main__":
    main()

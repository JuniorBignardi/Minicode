"""Oráculo da Parte 2: confere casos de teste e testes do agente contra a solução de referência.

A referência de cada tarefa foi validada contra o verificador oculto (validar_referencias.py), então
o que ela devolve é, por definição, o valor esperado correto.

Como funciona, em quatro passos:
  1. monta uma pasta temporária com os arquivos da tarefa e a solução de referência por cima;
  2. executa a entrada de cada caso (uma expressão Python) em um processo separado, com tempo limite;
  3. compara o valor obtido com o `esperado` do caso;
  4. dá a nota do caso: "correto", "errado" ou "inavaliavel" (a referência nem consegue rodar a entrada).
"""
import ast
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "eval_tasks"))

import tarefas_dificeis
import tarefas_faceis
from referencias_dificeis import REFERENCIAS_DIFICEIS
from referencias_faceis import REFERENCIAS_FACEIS

# tempo máximo, em segundos, para executar uma entrada (ou todas as de um plano, em executar_entradas)
TIMEOUT = 30

# entradas que a referência nem consegue executar (arquivo que não existe, nome desconhecido...):
# não dá para dizer que o valor esperado está errado
NAO_AVALIAVEIS = {"NameError", "SyntaxError", "FileNotFoundError", "ModuleNotFoundError", "ImportError"}

# Roda uma entrada (uma expressão, ou vários comandos terminando em uma expressão) com os módulos do
# projeto importados, e imprime em JSON o valor repr ou o nome da exceção.
SCRIPT = """
import ast, json, sys
entrada, modulos = sys.argv[1], json.loads(sys.argv[2])
espaco = {}
try:
    for m in modulos:
        exec("from " + m + " import *", espaco)
    arvore = ast.parse(entrada)
    ultimo = None
    if arvore.body and isinstance(arvore.body[-1], ast.Expr):
        ultimo = ast.Expression(arvore.body.pop().value)
    exec(compile(arvore, "<entrada>", "exec"), espaco)
    valor = eval(compile(ultimo, "<entrada>", "eval"), espaco) if ultimo else None
    print(json.dumps({"ok": True, "repr": repr(valor)}))
except BaseException as erro:
    print(json.dumps({"ok": False, "excecao": type(erro).__name__}))
"""

# Mesma ideia do SCRIPT, para várias entradas em um processo só (cada entrada com o seu espaço de nomes).
SCRIPT_VARIAS = """
import ast, json, sys
entradas, modulos = json.loads(sys.argv[1]), json.loads(sys.argv[2])
resultados = []
for entrada in entradas:
    espaco = {}
    try:
        for m in modulos:
            exec("from " + m + " import *", espaco)
        arvore = ast.parse(entrada)
        ultimo = None
        if arvore.body and isinstance(arvore.body[-1], ast.Expr):
            ultimo = ast.Expression(arvore.body.pop().value)
        exec(compile(arvore, "<entrada>", "exec"), espaco)
        valor = eval(compile(ultimo, "<entrada>", "eval"), espaco) if ultimo else None
        resultados.append({"ok": True, "repr": repr(valor)})
    except BaseException as erro:
        resultados.append({"ok": False, "excecao": type(erro).__name__})
print(json.dumps(resultados))
"""


# ---------- tarefa, referência e pasta temporária ----------

def tarefa_e_referencia(conjunto, id):
    # a tarefa (com os arquivos iniciais) e os arquivos da solução de referência, do conjunto "facil" ou "dificil"
    modulo, referencias = (
        (tarefas_faceis, REFERENCIAS_FACEIS) if conjunto == "facil" else (tarefas_dificeis, REFERENCIAS_DIFICEIS)
    )
    tarefa = next(t for t in modulo.TAREFAS if t["id"] == id)
    return tarefa, referencias[id]


def ambiente():
    # sem as variáveis do MiniCode (a chave de API não chega a código gerado por LLM) e sem .pyc
    env = {nome: valor for nome, valor in os.environ.items() if not nome.startswith("MINICODE_")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    return env


def escrever(pasta, arquivos):
    for caminho, conteudo in arquivos.items():
        (pasta / caminho).parent.mkdir(parents=True, exist_ok=True)
        (pasta / caminho).write_text(conteudo, encoding="utf-8")


def montar_projeto(conjunto, id, destino):
    # os arquivos iniciais da tarefa com a solução de referência por cima
    tarefa, referencia = tarefa_e_referencia(conjunto, id)
    escrever(destino, {**tarefa["arquivos"], **referencia})
    return destino


def e_teste(caminho):
    # arquivo de teste (test_*.py, *_test.py ou dentro de uma pasta tests): fica fora dos módulos importados
    nome = Path(caminho).name
    return nome.startswith("test_") or nome.endswith("_test.py") or "tests" in Path(caminho).parts[:-1]


# ---------- executar as entradas dos casos na referência ----------

def executar_entrada(projeto, entrada):
    # executa UMA entrada em um processo novo; devolve {"ok": True, "repr": ...} ou {"ok": False, "excecao": ...}
    modulos = [p.stem for p in Path(projeto).glob("*.py") if not e_teste(p.name)]
    try:
        r = subprocess.run(
            [sys.executable, "-c", SCRIPT, entrada, json.dumps(modulos)],
            cwd=projeto,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
            env=ambiente(),
        )
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError):
        return {"ok": False, "excecao": "SyntaxError"}   # não deu para avaliar


def executar_entradas(projeto, entradas):
    # uma saída por entrada, em um processo só. Se o processo travar ou quebrar, todas viram "não avaliável".
    modulos = [p.stem for p in Path(projeto).glob("*.py") if not e_teste(p.name)]
    try:
        r = subprocess.run(
            [sys.executable, "-c", SCRIPT_VARIAS, json.dumps(entradas), json.dumps(modulos)],
            cwd=projeto,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
            env=ambiente(),
        )
        saidas = json.loads(r.stdout.strip().splitlines()[-1])
        if len(saidas) == len(entradas):
            return saidas
    except (subprocess.TimeoutExpired, json.JSONDecodeError, IndexError):
        pass
    return [{"ok": False, "excecao": "SyntaxError"} for _ in entradas]


# ---------- comparar o valor obtido com o esperado ----------

def valor_literal(texto):
    # (True, valor) se o texto é um literal Python (número, texto, lista...); (False, None) se não for
    try:
        return True, ast.literal_eval(texto.strip())
    except (ValueError, SyntaxError):
        return False, None


def iguais(a, b):
    # números decimais: comparação com tolerância; o resto: mesmo valor e mesmo tipo (1 não é igual a True)
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
        except TypeError:
            return False
    return a == b and type(a) == type(b)


def comparar(resposta, esperado):
    # 'correto', 'errado' ou 'inavaliavel'
    esperado = str(esperado).strip()

    # caso 1: a referência levantou uma exceção
    if not resposta["ok"]:
        nome = resposta["excecao"]
        if nome in NAO_AVALIAVEIS:
            return "inavaliavel"
        return "correto" if nome in esperado else "errado"   # a referência levanta: o esperado deve citar a exceção

    # caso 2: a referência devolveu um valor; compara como literal Python
    _, obtido = valor_literal(resposta["repr"])
    leu, previsto = valor_literal(esperado)
    if leu and valor_literal(resposta["repr"])[0]:
        return "correto" if iguais(previsto, obtido) else "errado"

    # caso 3: valor que não é literal (objeto, texto solto): compara o texto
    texto_obtido = obtido if isinstance(obtido, str) else resposta["repr"]
    return "correto" if esperado.strip("'\"") == texto_obtido else "errado"


# ---------- avaliar um plano de testes e os testes do agente ----------

def avaliar_casos(conjunto, id, casos):
    # uma avaliação para cada caso do plano de testes: 'correto', 'errado' ou 'inavaliavel'
    pasta = Path(tempfile.mkdtemp())
    try:
        montar_projeto(conjunto, id, pasta)
        return [comparar(executar_entrada(pasta, c["entrada"]), c["esperado"]) for c in casos]
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def rodar_pytest(projeto, alvos=()):
    # (passou, conjunto de testes que falharam ou deram erro)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no", "-rfE", *alvos],
        cwd=projeto,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        env=ambiente(),
    )
    falhas = set(re.findall(r"^(?:FAILED|ERROR) (\S+)", r.stdout, re.M))
    return r.returncode == 0, falhas


def testes_errados_do_agente(conjunto, id, projeto_final, arquivos_de_teste):
    # Os testes que o agente escreveu, rodados contra a REFERÊNCIA: o que falha aqui é teste errado.
    pasta = Path(tempfile.mkdtemp())
    try:
        montar_projeto(conjunto, id, pasta)
        copiados = []
        for caminho in arquivos_de_teste:
            origem = Path(projeto_final) / caminho
            if origem.is_file() and caminho not in tarefa_e_referencia(conjunto, id)[0]["arquivos"]:
                (pasta / caminho).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(origem, pasta / caminho)
                copiados.append(caminho)
        if not copiados:
            return set()
        return rodar_pytest(pasta, copiados)[1]
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def veredito_do_oraculo(conjunto, id, snapshot):
    # Quem estava errado quando o agente pediu o diagnóstico: o código ou o teste?
    # Roda todos os testes do projeto com o código do agente (F1) e com a referência no lugar (F2).
    # Os que falham nas duas versões são testes errados; os que só falham no código do agente, código errado.
    tarefa, referencia = tarefa_e_referencia(conjunto, id)
    if any(e_teste(caminho) for caminho in referencia):
        return "nao_aplicavel"   # a tarefa pede testes: não há código de referência para trocar

    a, b = Path(tempfile.mkdtemp()), Path(tempfile.mkdtemp())
    try:
        for destino in (a, b):
            shutil.copytree(snapshot, destino, dirs_exist_ok=True)
        escrever(b, referencia)
        f1, f2 = rodar_pytest(a)[1], rodar_pytest(b)[1]
    finally:
        shutil.rmtree(a, ignore_errors=True)
        shutil.rmtree(b, ignore_errors=True)

    if not f1:
        return "sem_falha"
    if f1 <= f2:
        return "TEST_BUG"
    if not (f1 & f2):
        return "CODE_BUG"
    return "MISTO"

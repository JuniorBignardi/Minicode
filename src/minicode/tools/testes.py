import os
import re
import subprocess
import sys

from minicode.tools.files import cortar

TIMEOUT_TESTES = 120

# Os testes executam código escrito pela LLM. Por isso o pytest recebe só estas variáveis de
# ambiente (as que o Python e o pytest precisam): chaves de API e outros segredos não passam.
VARIAVEIS_PERMITIDAS = [
    "PATH", "PATHEXT", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC",
    "TEMP", "TMP", "TMPDIR", "HOME", "USERPROFILE", "LANG", "LC_ALL",
]


def ambiente_restrito():
    # só as variáveis de ambiente permitidas; o Python lê e escreve em UTF-8
    ambiente = {nome: valor for nome, valor in os.environ.items() if nome in VARIAVEIS_PERMITIDAS}
    ambiente["PYTHONUTF8"] = "1"
    ambiente["PYTHONIOENCODING"] = "utf-8"
    return ambiente


def nomes_dos_testes_que_falharam(saida):
    # Nomes das funções de teste que falharam, lidos dos títulos "____ test_x ____" do pytest.
    nomes = []
    for titulo in re.findall(r"^_{3,} (.+?) _{3,}$", saida, re.M):
        nome = titulo.split("[")[0].split(".")[-1].strip()   # tira parâmetros e o nome da classe
        if nome.startswith("test") and nome not in nomes:
            nomes.append(nome)
    return nomes


def arquivos_dos_testes_que_falharam(saida):
    # Caminhos dos arquivos dos testes que falharam, lidos das linhas "FAILED tests/x.py::nome" do pytest.
    arquivos = []
    for caminho in re.findall(r"^FAILED (\S+?)::", saida, re.M):
        caminho = caminho.replace("\\", "/")
        if caminho not in arquivos:
            arquivos.append(caminho)
    return arquivos


def run_tests(raiz, todos=False):
    # roda o pytest dentro do projeto e devolve (passou, saida)
    # Por padrão para no primeiro teste que falha (-x); com todos=True roda todos e lista todas as falhas.
    # A saída do pytest é lida como UTF-8. Sem isso, no Windows ela era decodificada como
    # cp1252 e os acentos chegavam à LLM corrompidos ("maçã" virava "maÃ§Ã£").
    ambiente = ambiente_restrito()

    try:
        resultado = subprocess.run(
            [sys.executable, "-m", "pytest", "-q"] + ([] if todos else ["-x"]),
            cwd=raiz,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=ambiente,
            timeout=TIMEOUT_TESTES,
        )
    except subprocess.TimeoutExpired:
        return False, f"ERRO: os testes passaram de {TIMEOUT_TESTES}s"

    # código de retorno 0 significa que todos os testes passaram
    passou = resultado.returncode == 0
    return passou, cortar(resultado.stdout + resultado.stderr)

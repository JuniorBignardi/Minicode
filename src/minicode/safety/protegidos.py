import os
from pathlib import Path

from minicode.safety.caminhos import IGNORAR


def e_arquivo_de_teste(caminho_relativo):
    # test_*.py, *_test.py, conftest.py ou qualquer .py dentro de uma pasta tests/
    nome = caminho_relativo.name
    if not nome.endswith(".py"):
        return False

    if nome.startswith("test_") or nome.endswith("_test.py") or nome == "conftest.py":
        return True

    return "tests" in caminho_relativo.parts[:-1]


def listar_testes(raiz):
    # devolve os testes que já existem no projeto (caminhos relativos, com "/")
    raiz = Path(raiz).resolve()
    testes = []

    for pasta, subpastas, arquivos in os.walk(raiz):
        subpastas[:] = [p for p in subpastas if p not in IGNORAR]
        for arquivo in arquivos:
            relativo = (Path(pasta) / arquivo).relative_to(raiz)
            if e_arquivo_de_teste(relativo):
                testes.append(relativo.as_posix())

    return sorted(testes)

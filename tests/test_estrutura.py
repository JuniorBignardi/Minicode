from pathlib import Path

# Regra de código limpo do projeto: nenhum arquivo de código passa de 400 linhas.
# Se um arquivo crescer demais, divida-o em módulos coesos (veja como o orquestrador foi dividido).
LIMITE_DE_LINHAS = 400

RAIZ = Path(__file__).resolve().parent.parent


def test_nenhum_arquivo_de_codigo_passa_do_limite_de_linhas():
    grandes = []
    for pasta in ("src", "eval_tasks", "examples"):
        for arquivo in (RAIZ / pasta).rglob("*.py"):
            linhas = len(arquivo.read_text(encoding="utf-8").splitlines())
            if linhas > LIMITE_DE_LINHAS:
                grandes.append(f"{arquivo.relative_to(RAIZ).as_posix()}: {linhas} linhas")

    assert not grandes, "arquivos acima do limite de " + str(LIMITE_DE_LINHAS) + " linhas:\n" + "\n".join(grandes)

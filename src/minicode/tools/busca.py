from pathlib import Path

from minicode.safety.caminhos import IGNORAR
from minicode.tools.files import cortar, resolver

MAX_RESULTADOS = 50


def search_code(raiz, padrao, diretorio="."):
    # procura um trecho de texto (sem diferenciar maiúsculas) nos arquivos de texto do projeto
    if not padrao:
        return False, "ERRO: o padrão de busca está vazio"

    pasta, erro = resolver(raiz, diretorio)
    if erro:
        return False, erro
    if not pasta.is_dir():
        return False, f"ERRO: {diretorio} não é uma pasta"

    raiz = Path(raiz).resolve()
    achados = []
    for arquivo in sorted(pasta.rglob("*")):
        relativo = arquivo.relative_to(raiz)
        if not arquivo.is_file() or any(parte in IGNORAR for parte in relativo.parts):
            continue

        try:
            linhas = arquivo.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue  # arquivo binário ou ilegível

        for numero, linha in enumerate(linhas, start=1):
            if padrao.lower() in linha.lower():
                achados.append(f"{relativo.as_posix()}:{numero}: {linha.strip()}")

    if not achados:
        return True, f"nenhum resultado para '{padrao}'"

    texto = "\n".join(achados[:MAX_RESULTADOS])
    if len(achados) > MAX_RESULTADOS:
        texto += f"\n... ({len(achados)} resultados, mostrando os {MAX_RESULTADOS} primeiros)"
    return True, cortar(texto)

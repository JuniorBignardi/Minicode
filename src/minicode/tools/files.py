from pathlib import Path

from minicode.safety.caminhos import IGNORAR, validar_caminho

# Toda ferramenta recebe a raiz do projeto como primeiro argumento
# e devolve (ok, texto): ok diz se deu certo, texto vai de volta para a LLM.

LIMITE_TEXTO = 5000


def cortar(texto):
    # evita mandar textos enormes para a LLM
    if len(texto) > LIMITE_TEXTO:
        return texto[:LIMITE_TEXTO] + "\n... (texto cortado)"
    return texto


def resolver(raiz, caminho):
    # devolve (caminho absoluto, None), ou (None, mensagem de erro) se ele sair do projeto
    try:
        return validar_caminho(raiz, caminho), None
    except ValueError as erro:
        return None, f"ERRO: {erro}"


def list_files(raiz, diretorio="."):
    pasta, erro = resolver(raiz, diretorio)
    if erro:
        return False, erro
    if not pasta.is_dir():
        return False, f"ERRO: {diretorio} não é uma pasta"

    raiz = Path(raiz).resolve()
    arquivos = []
    for caminho in sorted(pasta.rglob("*")):
        relativo = caminho.relative_to(raiz)
        if caminho.is_file() and not (set(relativo.parts) & IGNORAR):
            arquivos.append(relativo.as_posix())

    if not arquivos:
        return True, "(nenhum arquivo)"
    return True, cortar("\n".join(arquivos))


def read_file(raiz, path):
    arquivo, erro = resolver(raiz, path)
    if erro:
        return False, erro
    if not arquivo.is_file():
        return False, f"ERRO: arquivo não encontrado: {path}"

    try:
        return True, cortar(arquivo.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return False, f"ERRO: {path} não é um arquivo de texto"


def create_file(raiz, path, content):
    # cria um arquivo NOVO: se ele já existe, recusa (para alterar um arquivo existente é o write_file)
    arquivo, erro = resolver(raiz, path)
    if erro:
        return False, erro
    if arquivo.exists():
        return False, f"ERRO: {path} já existe. Para sobrescrevê-lo use write_file, com o conteúdo completo."

    return write_file(raiz, path, content)


def write_file(raiz, path, content):
    arquivo, erro = resolver(raiz, path)
    if erro:
        return False, erro

    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text(content, encoding="utf-8")
    return True, f"arquivo {path} escrito ({len(content.splitlines())} linhas)"

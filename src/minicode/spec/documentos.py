import re

MIN_CRITERIOS = 2
MIN_PASSOS = 2


def extrair_documento(texto, tag):
    # pega o que está entre <tag> e </tag>; o ? faz pegar só o primeiro bloco
    padrao = f"<{tag}>(.*?)</{tag}>"
    achou = re.search(padrao, texto, re.DOTALL)
    if achou is None:
        return None
    return achou.group(1).strip()


def arquivos_citados(texto):
    # arquivos .py citados no pedido do usuário (ex.: "no arquivo fatorial.py"), sem repetição
    citados = []
    for caminho in re.findall(r"[\w./\\-]+\.py\b", texto):
        caminho = caminho.replace("\\", "/")
        if caminho not in citados:
            citados.append(caminho)
    return citados


def contar_itens(texto):
    # conta as linhas de lista: "- item", "* item", "1. item" ou "1) item"
    total = 0
    for linha in texto.splitlines():
        linha = linha.strip()
        if linha.startswith("-") or linha.startswith("*") or re.match(r"\d+[.)]", linha):
            total += 1
    return total


def validar_spec(texto):
    if "## Objective" not in texto:
        return False, "falta a seção '## Objective'"

    if "## Acceptance Criteria" not in texto:
        return False, "falta a seção '## Acceptance Criteria'"

    # a seção de critérios vai até o próximo título "## " (ou até o fim)
    criterios = texto.split("## Acceptance Criteria")[1]
    criterios = criterios.split("\n## ")[0]

    if contar_itens(criterios) < MIN_CRITERIOS:
        return False, f"escreva pelo menos {MIN_CRITERIOS} critérios de aceitação, um por linha começando com '-'"

    return True, ""


def validar_plano(texto):
    if contar_itens(texto) < MIN_PASSOS:
        return False, f"o plano precisa de pelo menos {MIN_PASSOS} passos numerados"

    return True, ""

from pathlib import Path

# pastas que não fazem parte do projeto: o agente não precisa vê-las nem percorrê-las
IGNORAR = {".git", ".venv", "venv", "__pycache__", ".minicode", ".pytest_cache", "node_modules"}


def validar_caminho(raiz, caminho):
    # junta a raiz com o caminho pedido e resolve ".." e links
    raiz = Path(raiz).resolve()
    alvo = (raiz / caminho).resolve()

    # se o resultado não está dentro da raiz, o caminho é recusado
    if not alvo.is_relative_to(raiz):
        raise ValueError(f"caminho fora do projeto: {caminho}")

    return alvo

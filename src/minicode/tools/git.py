import subprocess

from minicode.tools.files import cortar

TIMEOUT_GIT = 30


def git_diff(raiz):
    # o que mudou no projeto desde o último commit (precisa ser um repositório git)
    try:
        resultado = subprocess.run(
            ["git", "diff", "HEAD"], cwd=raiz, capture_output=True,
            encoding="utf-8", errors="replace", timeout=TIMEOUT_GIT,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "ERRO: não foi possível executar o git"

    if resultado.returncode != 0:
        return False, "ERRO: o projeto não é um repositório git (ou ainda não tem commits)"
    if not resultado.stdout.strip():
        return True, "nenhuma alteração desde o último commit"
    return True, cortar(resultado.stdout)

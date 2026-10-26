import shlex
import subprocess
import sys

from minicode.safety.comandos import validar_comando
from minicode.tools.files import cortar
from minicode.tools.testes import ambiente_restrito

TIMEOUT_COMANDO = 30


def run_command(raiz, comando):
    # Executa um comando dentro do projeto e devolve (passou, saída). O comando só roda depois de
    # passar pelo validador; não usa shell (sem pipes nem redirecionamentos) e recebe só as
    # variáveis de ambiente permitidas, como o pytest.
    if not isinstance(comando, str):
        return False, "ERRO: o comando precisa ser um texto"

    permitido, motivo = validar_comando(comando, raiz)
    if not permitido:
        return False, f"ERRO: comando recusado ({motivo})"

    partes = shlex.split(comando)
    if partes[0] in ("python", "python3"):
        partes[0] = sys.executable   # o mesmo Python (e as mesmas bibliotecas) que roda o agente

    try:
        resultado = subprocess.run(
            partes, cwd=raiz, capture_output=True, encoding="utf-8", errors="replace",
            env=ambiente_restrito(), timeout=TIMEOUT_COMANDO,
        )
    except FileNotFoundError:
        return False, f"ERRO: comando não encontrado: {partes[0]}"
    except subprocess.TimeoutExpired:
        return False, f"ERRO: o comando passou de {TIMEOUT_COMANDO}s"

    saida = (resultado.stdout + resultado.stderr).strip() or "(sem saída)"
    return resultado.returncode == 0, cortar(f"{saida}\n(código de saída {resultado.returncode})")

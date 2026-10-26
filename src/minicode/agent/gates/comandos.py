from pathlib import Path

from minicode.safety.caminhos import IGNORAR
from minicode.tools.comandos import run_command
from minicode.tracing.registro import registrar_evento

# Hard gate do run_command: o comando serve para rodar e experimentar o código, não para gravar
# arquivos. Gravar arquivos é papel de create_file e write_file, que passam por todos os gates de
# escrita. Por isso o programa fotografa o projeto antes do comando e desfaz o que ele alterou.

LIMITE_DO_ARQUIVO = 1_000_000


def fotografar(raiz):
    # arquivo (caminho relativo, com "/") -> bytes, dos arquivos do projeto que não são ignorados
    raiz = Path(raiz).resolve()
    arquivos = {}
    for caminho in raiz.rglob("*"):
        relativo = caminho.relative_to(raiz)
        if not caminho.is_file() or set(relativo.parts) & IGNORAR:
            continue
        if caminho.stat().st_size <= LIMITE_DO_ARQUIVO:
            arquivos[relativo.as_posix()] = caminho.read_bytes()
    return arquivos


def desfazer_alteracoes(raiz, antes):
    # volta o projeto ao estado da fotografia. Devolve os arquivos que o comando tinha alterado.
    raiz = Path(raiz).resolve()
    depois = fotografar(raiz)
    alterados = sorted(nome for nome in set(antes) | set(depois) if antes.get(nome) != depois.get(nome))

    for nome in alterados:
        alvo = raiz / nome
        if nome in antes:
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(antes[nome])
        else:
            alvo.unlink()
    return alterados


def executar_comando(raiz, args):
    # Roda o run_command e desfaz qualquer arquivo que ele tenha gravado. Devolve (ok, texto).
    try:
        antes = fotografar(raiz)
        ok, texto = run_command(raiz, **args)
    except TypeError:
        return False, "ERRO: argumentos inválidos para run_command"

    alterados = desfazer_alteracoes(raiz, antes)
    if alterados:
        registrar_evento(raiz, {"tipo": "comando_desfeito", "arquivos": alterados})
        texto += ("\nAVISO: o comando alterou arquivos e o sistema desfez a alteração "
                  f"({', '.join(alterados)}). Para gravar arquivos use create_file ou write_file.")
    return ok, texto

import re
import shlex

from minicode.safety.caminhos import validar_caminho

# comandos que nunca podem ser executados pelo agente
# pip e npm instalam pacotes da internet no computador: o agente não instala dependências
COMANDOS_PROIBIDOS = ["sudo", "shutdown", "reboot", "poweroff", "halt", "mkfs", "dd", "format", "pip", "pip3", "npm"]

# alvos que tornam um "rm -r" perigoso
ALVOS_PERIGOSOS = ["/", "~", "*", ".."]


def sai_do_projeto(raiz, parte):
    # um argumento que parece caminho (absoluto, "~", "..", letra de unidade) e aponta para fora do projeto
    if parte.startswith("~"):
        return True   # a pasta do usuário nunca é o projeto
    parece_caminho = parte.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", parte) or ".." in re.split(r"[\\/]", parte)
    if not parece_caminho:
        return False
    try:
        validar_caminho(raiz, parte)
    except ValueError:
        return True
    return False


def validar_comando(comando, raiz=None):
    # devolve (True, "") se pode executar, ou (False, motivo) se foi recusado
    # Com a raiz do projeto, também recusa argumentos que apontam para fora dela.
    try:
        partes = shlex.split(comando)
    except ValueError:
        return False, "comando mal formado"

    if not partes:
        return False, "comando vazio"

    for parte in partes:
        if parte in COMANDOS_PROIBIDOS:
            return False, f"comando proibido: {parte}"

    # rm com opção recursiva apontando para um alvo perigoso
    if partes[0] == "rm":
        recursivo = any(p.startswith("-") and "r" in p.lower() for p in partes[1:])
        alvos = [p for p in partes[1:] if not p.startswith("-")]
        if recursivo and any(alvo in ALVOS_PERIGOSOS for alvo in alvos):
            return False, "rm recursivo em alvo perigoso"

    if raiz is not None:
        # também o texto cru: o shlex consome as barras invertidas de "C:\Windows\x"
        for parte in partes + re.split(r"[\s\"']+", comando):
            if sai_do_projeto(raiz, parte):
                return False, f"caminho fora do projeto: {parte}"

    return True, ""

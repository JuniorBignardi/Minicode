import shlex

# comandos que nunca podem ser executados pelo agente
COMANDOS_PROIBIDOS = ["sudo", "shutdown", "reboot", "poweroff", "halt", "mkfs", "dd", "format"]

# alvos que tornam um "rm -r" perigoso
ALVOS_PERIGOSOS = ["/", "~", "*", ".."]


def validar_comando(comando):
    # devolve (True, "") se pode executar, ou (False, motivo) se foi recusado
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

    return True, ""

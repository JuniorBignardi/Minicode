import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from minicode.agent.escrita import diferenca_dos_originais
from minicode.agent.estados import DONE
from minicode.agent.orquestrador import rodar_agente
from minicode.tracing import tela

VARIAVEIS_DE_AMBIENTE = ("MINICODE_API_BASE", "MINICODE_API_KEY", "MINICODE_MODEL")
SAIR = ("/sair", "sair", "exit", "quit")


def conferir_ambiente():
    # O .env é lido aqui, antes de importar o cliente da LLM. Uma variável vazia (o .env.example copiado
    # e ainda não preenchido) conta como ausente: o usuário recebe uma mensagem clara, não um traceback.
    load_dotenv()
    faltando = [nome for nome in VARIAVEIS_DE_AMBIENTE if not os.environ.get(nome)]
    if faltando:
        print(f"Faltam variáveis de ambiente: {', '.join(faltando)}.")
        print("Preencha o arquivo .env (copie o .env.example) ou defina-as no terminal.")
        sys.exit(2)


def mostrar_arquivo(raiz, nome):
    arquivo = raiz / ".minicode" / nome
    if arquivo.is_file():
        tela.escrever(arquivo.read_text(encoding="utf-8"))
    else:
        tela.aviso(f"ainda não existe {nome}: rode uma tarefa primeiro")


def mostrar_log(raiz):
    arquivo = raiz / ".minicode" / "actions.jsonl"
    if not arquivo.is_file():
        tela.aviso("ainda não existe registro: rode uma tarefa primeiro")
        return

    for linha in arquivo.read_text(encoding="utf-8").splitlines()[-15:]:
        evento = json.loads(linha)
        tipo = evento.pop("tipo")
        resto = " ".join(f"{chave}={tela.resumir(valor, 40)}" for chave, valor in evento.items())
        tela.escrever(f"  {tipo:24} {resto}")


def comando(texto, raiz, ultima):
    # comandos que começam com "/"; ultima é a execução anterior (ou None)
    if texto == "/ajuda":
        tela.ajuda()
    elif texto == "/spec":
        mostrar_arquivo(raiz, "specification.md")
    elif texto == "/plano":
        mostrar_arquivo(raiz, "plan.md")
        mostrar_arquivo(raiz, "test_plan.md")
    elif texto == "/log":
        mostrar_log(raiz)
    elif texto == "/diff":
        diff = diferenca_dos_originais(ultima, raiz) if ultima else ""
        tela.escrever(diff or "(nenhum arquivo que já existia foi alterado)")
    else:
        tela.aviso("comando desconhecido; digite /ajuda")


def rodar_tarefa(tarefa, raiz, chat):
    inicio = time.time()
    execucao = rodar_agente(tarefa, raiz, chat)
    tela.final(execucao, raiz, time.time() - inicio)
    return execucao


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")   # os símbolos e os acentos da tela precisam de UTF-8

    # o cliente é importado depois da conferência, para que importar este módulo não exija o .env
    conferir_ambiente()
    from minicode.llm.client import chat

    # o projeto é a pasta onde o comando foi executado
    raiz = Path.cwd()

    # minicode "pedido": roda uma tarefa e sai (código 0 se concluiu)
    if len(sys.argv) > 1:
        tela.cabecalho(raiz, os.environ["MINICODE_MODEL"])
        execucao = rodar_tarefa(" ".join(sys.argv[1:]), raiz, chat)
        sys.exit(0 if execucao.estado == DONE else 1)

    tela.cabecalho(raiz, os.environ["MINICODE_MODEL"])
    ultima = None
    while True:
        try:
            texto = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if texto in SAIR:
            break
        if not texto:
            continue
        if texto.startswith("/"):
            comando(texto, raiz, ultima)
            continue

        try:
            ultima = rodar_tarefa(texto, raiz, chat)
        except KeyboardInterrupt:
            tela.aviso("execução interrompida; os arquivos já gravados continuam no projeto")


if __name__ == "__main__":
    main()

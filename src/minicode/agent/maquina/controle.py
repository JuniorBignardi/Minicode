# Base do orquestrador: mudar o estado, encerrar a execução e funções usadas pelos outros passos.
# Só avancar() muda o estado da execução.

import re

from minicode.tools.files import read_file
from minicode.tracing import tela
from minicode.tracing.depuracao import depurar, instantaneo  # DEBUG
from minicode.tracing.registro import registrar_evento, salvar_estado


def avancar(execucao, raiz, novo):
    antigo = execucao.estado
    execucao.mudar_para(novo)  # os hard gates ficam em estados.py
    registrar_evento(raiz, {"tipo": "mudanca_estado", "de": antigo, "para": novo})
    salvar_estado(raiz, execucao)
    tela.estado(antigo, novo)
    depurar(execucao, raiz, "mudanca_estado", de=antigo, para=novo, **instantaneo(execucao))  # DEBUG


def finalizar(execucao, raiz):
    depurar(execucao, raiz, "fim", **instantaneo(execucao))  # DEBUG
    registrar_evento(raiz, {
        "tipo": "resultado_final",
        "estado": execucao.estado,
        "tentativas": execucao.tentativas,
        "iteracoes": execucao.iteracoes,
        "chamadas_llm": execucao.chamadas_llm,
    })
    salvar_estado(raiz, execucao)
    return execucao


def normalizar(saida):
    # A "assinatura" da falha, para saber se duas falhas são a mesma. Num pytest, são as linhas de
    # erro ("E   assert ..."): o nome do arquivo e do teste muda quando o modelo reescreve o teste
    # em outro arquivo, e o tempo muda sempre. Em outras saídas (relatórios de revisão) vale o texto.
    erros = [linha.strip() for linha in saida.splitlines() if linha.startswith("E ")]
    if erros:
        return "\n".join(erros)
    return re.sub(r"\d+\.\d+s", "", saida)


def estado_atual_dos_arquivos(raiz, arquivos):
    partes = []
    for caminho in arquivos:
        ok, texto = read_file(raiz, caminho)
        if ok:
            partes.append(f"--- {caminho}\n{texto}")
    return "\n\n".join(partes)

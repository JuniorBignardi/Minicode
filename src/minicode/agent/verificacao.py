# O estado VERIFYING: revisão do código, pytest e revisão dos testes, com o orçamento de veto.

from minicode.agent.controle import estado_atual_dos_arquivos
from minicode.agent.estados import MAX_VETOS_POR_CRITERIO
from minicode.agent.fases import cortar_registro
from minicode.agent.revisoes import rodar_revisao
from minicode.spec.revisao import assinatura_da_reprovacao
from minicode.tools.testes import run_tests
from minicode.tracing import tela
from minicode.tracing.depuracao import depurar  # DEBUG
from minicode.tracing.registro import registrar_evento


def veto_valido(execucao, raiz, quem, aprovada, relatorio):
    # Orçamento de veto: cada critério pode ser reprovado por um juiz LLM só MAX_VETOS_POR_CRITERIO
    # vezes com efeito. Depois disso a reprovação é dispensada (os testes continuam obrigatórios).
    # Devolve a aprovação final da revisão.
    if aprovada:
        return True

    criterios = assinatura_da_reprovacao(relatorio)
    if not criterios:
        return False   # relatório sem critérios identificáveis: a reprovação vale

    for criterio in criterios:
        chave = f"{quem}:{criterio}"
        execucao.vetos[chave] = execucao.vetos.get(chave, 0) + 1

    esgotados = [c for c in criterios if execucao.vetos[f"{quem}:{c}"] > MAX_VETOS_POR_CRITERIO]
    if len(esgotados) < len(criterios):
        return False

    registrar_evento(raiz, {"tipo": "revisao_dispensada", "revisao": quem, "criterios": criterios})
    tela.aviso(f"revisão {quem}: o veto desses critérios já foi usado; ela é dispensada e os testes decidem")
    return True


def revisar(execucao, chat, raiz, arquivos, tipo, nome):
    # Uma revisão (tipo "codigo" ou "testes") com o orçamento de veto aplicado, registrada e mostrada.
    # Devolve (aprovada, relatorio), ou None se a chamada à LLM falhou.
    revisao = rodar_revisao(execucao, chat, raiz, arquivos, tipo)
    if revisao is None:
        return None

    aprovada, relatorio = revisao
    aprovada = veto_valido(execucao, raiz, tipo, aprovada, relatorio)
    execucao.registrar_revisao(tipo, aprovada)
    tela.revisao(nome, aprovada, relatorio)
    return aprovada, relatorio


def verificar(execucao, chat, raiz):
    # O estado VERIFYING: três verificações, nesta ordem. Devolve (motivo, texto):
    #   motivo None            -> tudo aprovado
    #   "revisao_codigo"       -> o código não cumpre algum critério da spec (testes nem rodaram)
    #   "testes"               -> algum teste falhou
    #   "revisao_testes"       -> os testes passaram, mas não verificam algum critério da spec
    #   "erro"                 -> a chamada à LLM falhou (a execução já está em FAILED)
    arquivos = estado_atual_dos_arquivos(raiz, execucao.arquivos_alterados)
    depurar(execucao, raiz, "arquivos_para_verificacao", arquivos=execucao.arquivos_alterados,  # DEBUG
            caracteres=len(arquivos), truncado="(texto cortado)" in arquivos, conteudo=arquivos)  # DEBUG

    # 1. o código cumpre a spec? (a revisão só pode reprovar; nunca aprova sozinha)
    if execucao.exige_revisao:
        resultado = revisar(execucao, chat, raiz, arquivos, "codigo", "do código")
        if resultado is None:
            return "erro", ""
        aprovada, relatorio = resultado
        if not aprovada:
            return "revisao_codigo", relatorio

    # 2. quem roda os testes é o programa, não a LLM
    passou, saida = run_tests(raiz)
    execucao.registrar_testes(passou)
    registrar_evento(raiz, {"tipo": "testes", "passaram": passou, "saida": cortar_registro(saida)})
    depurar(execucao, raiz, "saida_testes", passou=passou, caracteres=len(saida),  # DEBUG
            cortado=saida.endswith("(texto cortado)"), saida=saida)  # DEBUG
    tela.testes(passou, saida)
    if not passou:
        return "testes", saida

    # 3. os testes verificam a spec de verdade?
    if execucao.exige_revisao:
        resultado = revisar(execucao, chat, raiz, arquivos, "testes", "dos testes")
        if resultado is None:
            return "erro", ""
        aprovada, relatorio = resultado
        if not aprovada:
            return "revisao_testes", relatorio

    return None, ""

# O orquestrador liga os passos na ordem do enunciado:
#   spec -> plano -> plano de testes -> implementação -> verificação -> (diagnóstico -> reparo) -> resultado
# Só ele decide a sequência; o estado só muda através de controle.avancar().

from pathlib import Path

from minicode.agent.controle import avancar, finalizar, normalizar
from minicode.agent.estados import (
    DONE,
    Execucao,
    IMPLEMENTING,
    REPAIRING,
    TransicaoInvalida,
    VERIFYING,
)
from minicode.agent.fases import rodar_fase_implementacao
from minicode.agent.planejamento import fazer_plano, fazer_plano_de_testes, fazer_spec
from minicode.agent.reparo import (
    acabaram_as_tentativas,
    anunciar_reparo,
    corrigir_plano_de_testes,
    diagnosticar_falha,
    montar_mensagens_do_reparo,
    remover_testes_errados,
)
from minicode.agent.revisoes import texto_do_plano_de_testes
from minicode.agent.verificacao import verificar
from minicode.safety.protegidos import listar_testes
from minicode.spec.diagnostico import PLAN_BUG
from minicode.spec.documentos import arquivos_citados
from minicode.spec.prompts import mensagens_implementacao
from minicode.tools.testes import nomes_dos_testes_que_falharam
from minicode.tracing import tela
from minicode.tracing.depuracao import depuracao_ligada, depurar, iniciar_depuracao, instantaneo  # DEBUG
from minicode.tracing.registro import iniciar_registro, registrar_evento, salvar_estado


def preparar_execucao(tarefa, raiz, max_tentativas, max_iteracoes, revisar_spec, modo_debug, diagnosticar):
    # Cria a Execucao com o que o programa já sabe antes de falar com a LLM e abre o registro.
    execucao = Execucao(tarefa, max_tentativas, max_iteracoes)
    execucao.depurar = depuracao_ligada() if modo_debug is None else modo_debug  # DEBUG
    execucao.exige_revisao = revisar_spec
    execucao.diagnosticar = diagnosticar
    execucao.raiz = raiz
    execucao.arquivos_exigidos = arquivos_citados(tarefa)
    execucao.arquivos_protegidos = listar_testes(raiz)
    iniciar_registro(raiz, tarefa)
    salvar_estado(raiz, execucao)
    if execucao.depurar:  # DEBUG
        iniciar_depuracao(raiz)  # DEBUG
        depurar(execucao, raiz, "inicio", tarefa=tarefa, max_tentativas=max_tentativas,  # DEBUG
                max_iteracoes=max_iteracoes, revisar_spec=revisar_spec, **instantaneo(execucao))  # DEBUG
    return execucao


def implementar_e_reparar(execucao, chat, raiz):
    # O laço central: implementar, verificar e, se falhou, diagnosticar e reparar.
    mensagens = mensagens_implementacao(
        execucao.tarefa, execucao.spec, execucao.plano, texto_do_plano_de_testes(execucao))
    falhas_vistas = set()   # assinaturas das falhas já vistas nesta execução
    ultimo_veredito = None  # o diagnóstico mais recente (o das tentativas já gastas)
    tela.etapa("implementacao", "Implementação")
    execucao.arquivos_vistos = set()   # as leituras da spec e do plano eram outras conversas

    while True:
        if not rodar_fase_implementacao(execucao, chat, mensagens, raiz):
            return  # a fase já marcou FAILED

        # a fase mudou o estado para VERIFYING; registramos aqui
        registrar_evento(raiz, {"tipo": "mudanca_estado", "de": IMPLEMENTING, "para": VERIFYING})
        salvar_estado(raiz, execucao)
        tela.estado(IMPLEMENTING, VERIFYING)
        tela.etapa("verificacao", "Verificação")

        motivo, saida = verificar(execucao, chat, raiz)
        if motivo == "erro":
            return  # a chamada à LLM falhou; já está em FAILED
        if motivo is None:
            avancar(execucao, raiz, DONE)
            return

        # essa falha já apareceu antes? Então o reparo (ou o que foi reparado) não resolveu a causa
        repetiu = normalizar(saida) in falhas_vistas
        falhas_vistas.add(normalizar(saida))
        if repetiu:
            registrar_evento(raiz, {"tipo": "reparo_sem_progresso"})

        # guarda quais testes falharam: se o diagnóstico apontar o teste, ele terá que mudar
        execucao.testes_que_falharam = nomes_dos_testes_que_falharam(saida) if motivo == "testes" else []

        # falha de teste: diagnostica antes de reparar (código, teste, plano, ambiente ou desconhecido)
        veredito = None
        if motivo == "testes" and execucao.diagnosticar and execucao.tentativas < execucao.max_tentativas:
            veredito = diagnosticar_falha(execucao, chat, raiz, saida, repetiu)
            if veredito is None:
                return  # a chamada à LLM falhou; já está em FAILED
            ultimo_veredito = veredito

            if veredito["classificacao"] == PLAN_BUG and not corrigir_plano_de_testes(execucao, chat, raiz, veredito, saida):
                return

        try:
            avancar(execucao, raiz, REPAIRING)
        except TransicaoInvalida:
            acabaram_as_tentativas(execucao, chat, raiz, motivo, ultimo_veredito)
            return

        anunciar_reparo(execucao, raiz, motivo, veredito)
        removidos = remover_testes_errados(execucao, raiz, veredito)
        mensagens = montar_mensagens_do_reparo(execucao, raiz, mensagens, saida, repetiu, motivo, veredito, removidos)
        avancar(execucao, raiz, IMPLEMENTING)


def rodar_agente(tarefa, raiz, chat, max_tentativas=3, max_iteracoes=40, revisar_spec=True, modo_debug=None,
                 diagnosticar=True, planejar_testes=True):
    raiz = Path(raiz).resolve()
    execucao = preparar_execucao(tarefa, raiz, max_tentativas, max_iteracoes, revisar_spec, modo_debug, diagnosticar)

    if not fazer_spec(execucao, chat, raiz):
        return finalizar(execucao, raiz)
    if not fazer_plano(execucao, chat, raiz):
        return finalizar(execucao, raiz)
    if planejar_testes and not fazer_plano_de_testes(execucao, chat, raiz):
        return finalizar(execucao, raiz)

    avancar(execucao, raiz, IMPLEMENTING)
    implementar_e_reparar(execucao, chat, raiz)
    return finalizar(execucao, raiz)

# Do pedido até o plano de testes: spec, plano e plano de testes.
# Cada passo devolve False se a execução falhou (o estado já está em FAILED).

from minicode.agent.controle import avancar
from minicode.agent.estados import PLANNED, SPECIFIED, TEST_PLANNED
from minicode.agent.fases import rodar_fase_documento
from minicode.agent.revisoes import rodar_plano_de_testes, rodar_revisao_spec
from minicode.spec.documentos import validar_plano, validar_spec
from minicode.spec.plano_de_testes import plano_de_testes_em_texto
from minicode.spec.prompts import mensagem_correcao_da_spec, mensagens_plano, mensagens_spec
from minicode.tracing import tela
from minicode.tracing.registro import registrar_evento, salvar_documento


# quantas vezes a spec pode ser reescrita depois de reprovada pela revisão contra o pedido
MAX_CORRECOES_DA_SPEC = 2


def fazer_spec(execucao, chat, raiz):
    # especificação, revisada contra o pedido do usuário
    tela.etapa("spec", "Especificação")
    mensagens = mensagens_spec(execucao.tarefa)
    for rodada in range(MAX_CORRECOES_DA_SPEC + 1):
        spec = rodar_fase_documento(execucao, chat, mensagens, raiz, "spec", validar_spec)
        if spec is None:
            return False
        if not execucao.exige_revisao:
            break

        revisao = rodar_revisao_spec(execucao, chat, raiz, execucao.tarefa, spec)
        if revisao is None:
            return False
        aprovada, relatorio = revisao
        tela.revisao("da especificação", aprovada, relatorio)
        if aprovada:
            break

        if rodada == MAX_CORRECOES_DA_SPEC:
            # a revisão só pode reprovar, e já se corrigiu o suficiente: segue com a última versão
            registrar_evento(raiz, {"tipo": "spec_reprovada_seguindo"})
            break
        mensagens.append({"role": "user", "content": mensagem_correcao_da_spec(relatorio)})

    execucao.spec = spec
    salvar_documento(raiz, "specification.md", spec)
    tela.documento("especificação", spec)
    avancar(execucao, raiz, SPECIFIED)
    return True


def fazer_plano(execucao, chat, raiz):
    tela.etapa("plan", "Plano")
    plano = rodar_fase_documento(execucao, chat, mensagens_plano(execucao.tarefa, execucao.spec), raiz, "plan", validar_plano)
    if plano is None:
        return False

    execucao.plano = plano
    salvar_documento(raiz, "plan.md", plano)
    tela.documento("plano", plano)
    avancar(execucao, raiz, PLANNED)
    return True


def fazer_plano_de_testes(execucao, chat, raiz):
    # os casos de teste e seus valores esperados, definidos antes do código
    tela.etapa("plano_de_testes", "Plano de testes")
    casos = rodar_plano_de_testes(execucao, chat, raiz, execucao.tarefa, execucao.plano)
    if casos is None:
        return False

    if casos:
        guardar_plano_de_testes(execucao, raiz, casos)
        avancar(execucao, raiz, TEST_PLANNED)
    else:
        registrar_evento(raiz, {"tipo": "plano_de_testes_ausente"})
    return True


def guardar_plano_de_testes(execucao, raiz, casos, titulo="plano de testes"):
    execucao.plano_de_testes = casos
    texto = plano_de_testes_em_texto(casos)
    salvar_documento(raiz, "test_plan.md", texto)
    tela.documento(titulo, texto)

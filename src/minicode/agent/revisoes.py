import json

from minicode.agent.fases import cortar_registro, pedir_resposta
from minicode.llm.esquema import formato_da_resposta
from minicode.spec.diagnostico import (
    ESQUEMA_DIAGNOSTICO, PLAN_BUG, UNKNOWN, ancorar_na_spec, interpretar_diagnostico, mensagens_diagnostico,
)
from minicode.spec.plano_de_testes import (
    ESQUEMA_REVISAO_PLANO_DE_TESTES, criterios_da_spec, esquema_plano_de_testes, interpretar_plano_de_testes,
    interpretar_revisao_plano_de_testes, mensagem_correcao_do_plano_de_testes, mensagens_plano_de_testes,
    mensagens_revisao_plano_de_testes, plano_de_testes_em_texto, validar_plano_de_testes,
)
from minicode.spec.revisao import (
    ESQUEMAS, ESQUEMA_REVISAO_SPEC, interpretar_revisao, interpretar_revisao_spec,
    mensagens_revisao, mensagens_revisao_spec,
)
from minicode.tracing.registro import registrar_evento

# quantas vezes o plano de testes pode ser reescrito (critério sem caso, valor esperado errado)
MAX_CORRECOES_DO_PLANO_DE_TESTES = 2

# Chamadas à LLM que não escrevem arquivos: revisões, plano de testes e diagnóstico.
# Todas pedem uma resposta em JSON Schema e quem decide é o programa, lendo os campos.


def texto_do_plano_de_testes(execucao):
    if not execucao.plano_de_testes:
        return None
    return plano_de_testes_em_texto(execucao.plano_de_testes)


def pedir_revisao(execucao, chat, raiz, fase, nome, mensagens, formato, interpretar):
    # Uma chamada de revisão. Devolve (aprovada, relatorio), ou None se a execução falhou
    # (erro na chamada à LLM ou limite de iterações).
    resposta = pedir_resposta(execucao, chat, mensagens, raiz, fase, formato)
    if resposta is None:
        return None

    resultado = interpretar(resposta)
    if resultado is None:
        # a revisão só pode reprovar: se não deu para interpretá-la, ela não bloqueia
        registrar_evento(raiz, {"tipo": "revisao_inconclusiva", "revisao": nome, "resposta": cortar_registro(resposta)})
        return True, ""

    aprovada, relatorio = resultado
    registrar_evento(raiz, {"tipo": "revisao", "revisao": nome, "aprovada": aprovada, "relatorio": cortar_registro(relatorio)})
    return aprovada, relatorio


def rodar_revisao(execucao, chat, raiz, arquivos, tipo):
    # Confronta o projeto com cada critério da spec. tipo: "codigo" (o código cumpre os
    # critérios?) ou "testes" (os testes os verificam?).
    mensagens = mensagens_revisao(tipo, execucao.spec, arquivos, texto_do_plano_de_testes(execucao), execucao.tarefa)
    formato = formato_da_resposta(ESQUEMAS[tipo], "revisao")
    return pedir_revisao(execucao, chat, raiz, "revisao", tipo, mensagens, formato, interpretar_revisao)


def rodar_revisao_spec(execucao, chat, raiz, tarefa, spec):
    # Confronta a spec com o pedido original do usuário.
    mensagens = mensagens_revisao_spec(tarefa, spec)
    formato = formato_da_resposta(ESQUEMA_REVISAO_SPEC, "revisao_spec")
    return pedir_revisao(execucao, chat, raiz, "revisao_spec", "spec", mensagens, formato, interpretar_revisao_spec)


def rodar_plano_de_testes(execucao, chat, raiz, tarefa, plano, correcao=None):
    # Define os casos de teste ANTES do código. Dois controles do programa: todo critério da spec
    # precisa ter caso (o schema só aceita critérios que existem) e uma revisão confere o valor
    # esperado de cada caso. Devolve a lista de casos ([] se não saiu nenhum utilizável), ou None
    # se a execução falhou.
    # correcao: (casos_atuais, motivo) quando é a correção de um plano que um teste mostrou estar errado.
    criterios = criterios_da_spec(execucao.spec)
    mensagens = mensagens_plano_de_testes(tarefa, execucao.spec, plano)
    if correcao:
        casos_atuais, motivo = correcao
        mensagens.append({"role": "assistant", "content": json.dumps({"casos": casos_atuais}, ensure_ascii=False)})
        mensagens.append({"role": "user", "content": mensagem_correcao_do_plano_de_testes(motivo)})
    formato = formato_da_resposta(esquema_plano_de_testes(criterios), "plano_de_testes")
    formato_revisao = formato_da_resposta(ESQUEMA_REVISAO_PLANO_DE_TESTES, "revisao_plano_de_testes")

    casos = []
    for rodada in range(MAX_CORRECOES_DO_PLANO_DE_TESTES + 1):
        resposta = pedir_resposta(execucao, chat, mensagens, raiz, "plano_de_testes", formato)
        if resposta is None:
            return None

        casos = interpretar_plano_de_testes(resposta) or []
        valido, problema = validar_plano_de_testes(criterios, casos)

        if valido and not execucao.exige_revisao:
            return casos

        if valido:
            revisao = pedir_revisao(
                execucao, chat, raiz, "revisao_plano_de_testes", "plano_de_testes",
                mensagens_revisao_plano_de_testes(execucao.spec, casos), formato_revisao,
                interpretar_revisao_plano_de_testes)
            if revisao is None:
                return None
            aprovada, relatorio = revisao
            if aprovada:
                return casos
            problema = f"a revisão encontrou casos com resultado esperado errado:\n{relatorio}"

        registrar_evento(raiz, {"tipo": "plano_de_testes_reprovado", "problema": cortar_registro(problema)})
        if rodada == MAX_CORRECOES_DO_PLANO_DE_TESTES:
            break
        mensagens.append({"role": "assistant", "content": resposta})
        mensagens.append({"role": "user", "content": mensagem_correcao_do_plano_de_testes(problema)})

    # já se corrigiu o suficiente: segue com a última versão que tem casos (ou sem plano)
    registrar_evento(raiz, {"tipo": "plano_de_testes_reprovado_seguindo", "casos": len(casos)})
    return casos


def rodar_diagnostico(execucao, chat, raiz, arquivos, saida_testes):
    # Classifica a falha dos testes (CODE_BUG, TEST_BUG, PLAN_BUG, ENVIRONMENT_ERROR ou UNKNOWN)
    # numa chamada própria, em contexto limpo. Devolve o diagnóstico (dict), ou None se a
    # execução falhou.
    mensagens = mensagens_diagnostico(execucao.spec, arquivos, saida_testes, texto_do_plano_de_testes(execucao), execucao.tarefa)
    formato = formato_da_resposta(ESQUEMA_DIAGNOSTICO, "diagnostico")

    resposta = pedir_resposta(execucao, chat, mensagens, raiz, "diagnostico", formato)
    if resposta is None:
        return None

    diagnostico = interpretar_diagnostico(resposta)
    if diagnostico is None:
        # sem diagnóstico utilizável, o reparo segue sem restrições
        registrar_evento(raiz, {"tipo": "diagnostico_inconclusivo", "resposta": cortar_registro(resposta)})
        return {"classificacao": UNKNOWN, "citacao_da_spec": "",
                "evidencias": "(o diagnóstico não pôde ser interpretado)", "proxima_acao": ""}

    # PLAN_BUG só existe se há um plano de testes
    if diagnostico["classificacao"] == PLAN_BUG and not execucao.plano_de_testes:
        diagnostico = dict(diagnostico, classificacao=UNKNOWN)

    # evidência verificável: CODE_BUG, TEST_BUG e PLAN_BUG só valem se a citação existir de verdade na spec
    diagnostico, rebaixado = ancorar_na_spec(diagnostico, execucao.spec)
    if rebaixado:
        registrar_evento(raiz, {"tipo": "diagnostico_rebaixado", "evidencias": cortar_registro(diagnostico["evidencias"])})

    registrar_evento(raiz, {"tipo": "diagnostico", **diagnostico})
    return diagnostico

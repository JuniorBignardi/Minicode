# Diagnóstico e reparo: quem errou (código, teste ou plano), o que fazer e como montar a nova conversa.

from minicode.agent.controle import avancar, estado_atual_dos_arquivos
from minicode.agent.escrita import diferenca_dos_originais, remover_testes_que_falharam
from minicode.agent.estados import DIAGNOSING, DONE, FAILED, TEST_PLANNED
from minicode.agent.fases import cortar_registro
from minicode.agent.planejamento import guardar_plano_de_testes
from minicode.agent.revisoes import rodar_diagnostico, rodar_plano_de_testes, texto_do_plano_de_testes
from minicode.agent.verificacao import revisar
from minicode.spec.diagnostico import CODE_BUG, ENVIRONMENT_ERROR, PLAN_BUG, TEST_BUG, UNKNOWN
from minicode.spec.prompts import bloco_das_mudancas, mensagem_reparo, mensagens_recomeco
from minicode.tools.testes import arquivos_dos_testes_que_falharam, nomes_dos_testes_que_falharam, run_tests
from minicode.tracing import tela
from minicode.tracing.depuracao import depurar  # DEBUG
from minicode.tracing.registro import registrar_evento


# como cada motivo de reparo aparece para o usuário
MOTIVOS_DO_REPARO = {
    "testes": "os testes falharam",
    "revisao_codigo": "a revisão do código reprovou",
    "revisao_testes": "a revisão dos testes reprovou",
}


# Para cada diagnóstico: em que etapa está o erro e o que o reparo vai fazer
ETAPA_E_ACAO = {
    CODE_BUG: ("IMPLEMENTING (código)", "corrigir o código; só arquivos de código podem mudar"),
    TEST_BUG: ("IMPLEMENTING (testes)", "remover e reescrever o teste; o plano de testes continua valendo"),
    PLAN_BUG: ("TEST_PLANNED (plano de testes)", "corrigir o plano e reescrever o teste a partir dele"),
    ENVIRONMENT_ERROR: ("indefinida", "reparo sem restrição de arquivos"),
    UNKNOWN: ("indefinida", "reparo sem restrição de arquivos"),
}


def culpar_o_codigo_se_o_teste_ja_existia(execucao, raiz, saida, veredito):
    # Hierarquia de confiança: um teste que já existia no projeto é o oráculo confiável e nunca é o
    # culpado. Se ele falha, o código do agente quebrou comportamento existente (ex.: sobrescreveu um
    # arquivo e perdeu métodos), mesmo que o diagnóstico da LLM culpe o teste.
    antigos = [a for a in arquivos_dos_testes_que_falharam(saida) if a in execucao.arquivos_protegidos]
    if not antigos or veredito["classificacao"] == CODE_BUG:
        return veredito

    registrar_evento(raiz, {"tipo": "diagnostico_corrigido_pelo_programa", "teste": antigos[0]})
    return dict(
        veredito, classificacao=CODE_BUG,
        evidencias=(f"(definido pelo programa: o teste que falhou, {antigos[0]}, já existia no projeto e é o "
                    "oráculo confiável; o código quebrou comportamento existente) " + veredito["evidencias"]),
        proxima_acao=("restaure o comportamento que o teste existente espera: veja no diff contra o original "
                      "o que você removeu ou renomeou, e mantenha o que já existia"))


def subir_para_o_plano_se_a_falha_repetiu(execucao, raiz, repetiu, veredito):
    # Escalonamento: o teste foi reescrito e a falha voltou idêntica. Reescrever o teste de novo
    # não adianta; a origem está uma etapa acima, no plano de testes de que ele deriva.
    if not (repetiu and veredito["classificacao"] == TEST_BUG and execucao.plano_de_testes):
        return veredito

    registrar_evento(raiz, {"tipo": "reparo_escalado", "de": TEST_BUG, "para": PLAN_BUG})
    return dict(veredito, classificacao=PLAN_BUG, evidencias=(
        "(escalado: o teste foi reescrito e a falha se repetiu idêntica, então a origem está no plano de testes) "
        + veredito["evidencias"]))


def diagnosticar_falha(execucao, chat, raiz, saida, repetiu):
    # Estado DIAGNOSING: classifica a falha dos testes. Devolve o diagnóstico (dict),
    # ou None se a chamada à LLM falhou.
    avancar(execucao, raiz, DIAGNOSING)
    arquivos = estado_atual_dos_arquivos(raiz, execucao.arquivos_alterados)
    veredito = rodar_diagnostico(execucao, chat, raiz, arquivos, saida)
    if veredito is None:
        return None

    # o programa corrige o diagnóstico da LLM quando há evidência melhor
    veredito = culpar_o_codigo_se_o_teste_ja_existia(execucao, raiz, saida, veredito)
    veredito = subir_para_o_plano_se_a_falha_repetiu(execucao, raiz, repetiu, veredito)

    # se o reparo anterior não mudou nada, o diagnóstico não pode prender o novo reparo
    execucao.registrar_diagnostico(veredito, restringir=not repetiu)
    registrar_evento(raiz, {"tipo": "restricao_do_reparo", "restricao": execucao.restricao_escrita})
    tela.diagnostico(veredito)
    depurar(execucao, raiz, "diagnostico", veredito=veredito,  # DEBUG
            restricao=execucao.restricao_escrita, repetiu=repetiu)  # DEBUG
    return veredito


def corrigir_plano_de_testes(execucao, chat, raiz, veredito, saida):
    # PLAN_BUG: o erro está na etapa TEST_PLANNED. O estado volta para ela e o plano é corrigido
    # com a evidência do diagnóstico. Devolve False se a chamada à LLM falhou.
    avancar(execucao, raiz, TEST_PLANNED)
    motivo = (
        "um teste que seguia o plano falhou, e um revisor concluiu que o plano contradiz a especificação "
        f"ou exige algo que ela não define.\n- trecho da especificação: {veredito['citacao_da_spec']}\n"
        f"- evidências: {veredito['evidencias']}\n- próxima ação: {veredito['proxima_acao']}\n"
        f"- saída do teste que falhou:\n{saida[:1500]}"
    )
    casos = rodar_plano_de_testes(execucao, chat, raiz, execucao.tarefa, execucao.plano, (execucao.plano_de_testes, motivo))
    if casos is None:
        return False

    if casos:
        guardar_plano_de_testes(execucao, raiz, casos, "plano de testes corrigido")
        registrar_evento(raiz, {"tipo": "plano_de_testes_corrigido"})
    return True


def descartar_testes_que_continuam_falhando(execucao, chat, raiz):
    # Hierarquia de confiança dos oráculos: os testes que já existiam no projeto são confiáveis; os
    # que o modelo escreveu, não. Quando as tentativas de reparo acabam e o diagnóstico aponta o
    # teste (e não o código), o programa descarta os testes do modelo que continuam falhando e
    # verifica de novo. O DONE continua exigindo testes passando; o descarte fica registrado.
    # Devolve True se a verificação final passou.
    passou, saida = run_tests(raiz, todos=True)
    execucao.testes_que_falharam = nomes_dos_testes_que_falharam(saida)
    removidos = remover_testes_que_falharam(execucao, raiz)
    if not removidos:
        return False   # o que falha é teste que já existia (confiável): não há o que descartar

    nomes = [nome for caminho, nome in removidos]
    execucao.testes_descartados += nomes
    registrar_evento(raiz, {"tipo": "testes_descartados", "testes": nomes})
    tela.aviso(f"as tentativas acabaram e o diagnóstico aponta o teste: descartados {', '.join(nomes)}")

    # o código continua sendo revisado; a revisão dos testes não, porque eles foram descartados de propósito
    if execucao.exige_revisao:
        arquivos = estado_atual_dos_arquivos(raiz, execucao.arquivos_alterados)
        resultado = revisar(execucao, chat, raiz, arquivos, "codigo", "do código")
        if resultado is None or not resultado[0]:
            return False
        execucao.registrar_revisao("testes", True)

    passou, saida = run_tests(raiz)
    execucao.registrar_testes(passou)
    registrar_evento(raiz, {"tipo": "testes", "passaram": passou, "saida": cortar_registro(saida)})
    tela.testes(passou, saida)
    return passou


def montar_mensagens_do_reparo(execucao, raiz, mensagens, saida, repetiu, motivo, veredito, removidos):
    # Devolve a conversa que a LLM verá no reparo.
    # Se a revisão do código aprovou o código e mesmo assim os testes falharam, o erro provavelmente
    # está nos testes: o reparo avisa o modelo disso (um diagnóstico estruturado substitui o aviso).
    codigo_aprovado = motivo == "testes" and execucao.revisoes["codigo"] is True and veredito is None
    if codigo_aprovado:
        registrar_evento(raiz, {"tipo": "dica_codigo_aprovado"})

    mudancas = diferenca_dos_originais(execucao, raiz)

    if removidos or execucao.tentativas >= execucao.max_tentativas:
        # recomeça a conversa só com o essencial, sem o histórico confuso (e sem o teste errado):
        # na última tentativa ou quando o sistema removeu os testes
        arquivos = estado_atual_dos_arquivos(raiz, execucao.arquivos_alterados)
        mensagens = mensagens_recomeco(
            execucao.tarefa, execucao.spec, execucao.plano, arquivos, saida, repetiu, motivo, codigo_aprovado,
            veredito, execucao.restricao_escrita, removidos, texto_do_plano_de_testes(execucao), mudancas)
        execucao.arquivos_vistos = set(execucao.arquivos_alterados)   # o "estado atual" mostra esses arquivos
        registrar_evento(raiz, {"tipo": "contexto_reiniciado"})
        como, texto = "contexto reiniciado", mensagens[1]["content"]
    else:
        texto = bloco_das_mudancas(mudancas) + mensagem_reparo(
            saida, repetiu, execucao.spec, motivo, codigo_aprovado, veredito, execucao.restricao_escrita)
        mensagens.append({"role": "user", "content": texto})
        como = "acrescentada ao histórico"

    depurar(execucao, raiz, "reparo_construido", como=como, motivo=motivo, repetiu=repetiu,  # DEBUG
            codigo_aprovado=codigo_aprovado, n_mensagens=len(mensagens), mensagem=texto)  # DEBUG
    return mensagens


def diagnostico_culpa_o_teste(veredito):
    return veredito is not None and veredito["classificacao"] in (TEST_BUG, PLAN_BUG)


def anunciar_reparo(execucao, raiz, motivo, veredito):
    # Cada reparo registra em que etapa estava o erro e o que será feito (rastreabilidade), e mostra
    # o mesmo ao usuário.
    culpado, etapa, acao = None, None, None
    if veredito is not None:
        culpado = veredito["classificacao"]
        etapa, acao = ETAPA_E_ACAO[culpado]
        registrar_evento(raiz, {"tipo": "reparo", "motivo": motivo, "culpado": culpado,
                                "etapa": etapa, "acao": acao, "tentativa": execucao.tentativas})
    tela.reparo(execucao.tentativas, execucao.max_tentativas, MOTIVOS_DO_REPARO[motivo], culpado, etapa, acao)


def remover_testes_errados(execucao, raiz, veredito):
    # O teste errado sai de cena para o modelo não copiá-lo de volta. Quem está errado decide o resto:
    #   TEST_BUG: o teste não seguiu o plano nem a spec -> o plano continua valendo
    #   PLAN_BUG: o teste seguiu um plano que contradiz a spec -> o plano já foi corrigido
    # Devolve [(arquivo, nome)] dos testes removidos.
    if not diagnostico_culpa_o_teste(veredito):
        return []

    removidos = remover_testes_que_falharam(execucao, raiz)
    if removidos:
        nomes = [nome for caminho, nome in removidos]
        registrar_evento(raiz, {"tipo": "testes_removidos", "testes": nomes})
        tela.aviso(f"o programa removeu o teste que falhou: {', '.join(nomes)}")
    return removidos


def acabaram_as_tentativas(execucao, chat, raiz, motivo, ultimo_veredito):
    # Sem tentativas de reparo. Se o diagnóstico culpava o teste, ainda há o recurso de descartar os
    # testes do modelo que seguem falhando; senão (ou se não bastar) a execução falha.
    if motivo == "testes" and diagnostico_culpa_o_teste(ultimo_veredito):
        if descartar_testes_que_continuam_falhando(execucao, chat, raiz):
            avancar(execucao, raiz, DONE)
            return

    if execucao.estado != FAILED:
        avancar(execucao, raiz, FAILED)
    tela.aviso("as tentativas de reparo acabaram")

import re
from pathlib import Path

from minicode.agent.escrita import diferenca_dos_originais, remover_testes_que_falharam
from minicode.agent.estados import (
    Execucao, MAX_VETOS_POR_CRITERIO, TransicaoInvalida,
    SPECIFIED, PLANNED, TEST_PLANNED, IMPLEMENTING, VERIFYING, DIAGNOSING, REPAIRING, DONE, FAILED,
)
from minicode.agent.fases import cortar_registro, rodar_fase_documento, rodar_fase_implementacao
from minicode.agent.revisoes import (
    rodar_diagnostico, rodar_plano_de_testes, rodar_revisao, rodar_revisao_spec, texto_do_plano_de_testes,
)
from minicode.safety.protegidos import listar_testes
from minicode.spec.revisao import assinatura_da_reprovacao
from minicode.spec.diagnostico import CODE_BUG, ENVIRONMENT_ERROR, PLAN_BUG, TEST_BUG, UNKNOWN
from minicode.spec.documentos import arquivos_citados, validar_plano, validar_spec
from minicode.spec.plano_de_testes import plano_de_testes_em_texto
from minicode.spec.prompts import (
    bloco_das_mudancas, mensagem_correcao_da_spec, mensagem_reparo, mensagens_implementacao, mensagens_plano,
    mensagens_recomeco, mensagens_spec,
)
from minicode.tools.files import read_file
from minicode.tools.testes import nomes_dos_testes_que_falharam, run_tests
from minicode.tracing import tela
from minicode.tracing.depuracao import depuracao_ligada, depurar, iniciar_depuracao, instantaneo  # DEBUG
from minicode.tracing.registro import (
    iniciar_registro, registrar_evento, salvar_documento, salvar_estado,
)

# quantas vezes a spec pode ser reescrita depois de reprovada pela revisão contra o pedido
MAX_CORRECOES_DA_SPEC = 2

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


# O orquestrador liga todas as peças na ordem do enunciado:
#   spec -> plano -> plano de testes -> implementação -> verificação -> (diagnóstico -> reparo) -> resultado
# Só ele muda o estado da execução, sempre através de avancar(). Cada passo devolve False se a
# execução falhou (o estado já está em FAILED), e rodar_agente então encerra.


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


# --- do pedido até o plano de testes ---

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


# --- verificação ---

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
        revisao = rodar_revisao(execucao, chat, raiz, arquivos, "codigo")
        if revisao is None:
            return "erro", ""
        aprovada, relatorio = revisao
        aprovada = veto_valido(execucao, raiz, "codigo", aprovada, relatorio)
        execucao.registrar_revisao("codigo", aprovada)
        tela.revisao("do código", aprovada, relatorio)
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
        revisao = rodar_revisao(execucao, chat, raiz, arquivos, "testes")
        if revisao is None:
            return "erro", ""
        aprovada, relatorio = revisao
        aprovada = veto_valido(execucao, raiz, "testes", aprovada, relatorio)
        execucao.registrar_revisao("testes", aprovada)
        tela.revisao("dos testes", aprovada, relatorio)
        if not aprovada:
            return "revisao_testes", relatorio

    return None, ""


# --- diagnóstico e reparo ---

def diagnosticar_falha(execucao, chat, raiz, saida, repetiu):
    # Estado DIAGNOSING: classifica a falha dos testes. Devolve o diagnóstico (dict),
    # ou None se a chamada à LLM falhou.
    avancar(execucao, raiz, DIAGNOSING)
    arquivos = estado_atual_dos_arquivos(raiz, execucao.arquivos_alterados)
    veredito = rodar_diagnostico(execucao, chat, raiz, arquivos, saida)
    if veredito is None:
        return None

    # Escalonamento: o teste foi reescrito e a falha voltou idêntica. Reescrever o teste de novo
    # não adianta; a origem está uma etapa acima, no plano de testes de que ele deriva.
    if repetiu and veredito["classificacao"] == TEST_BUG and execucao.plano_de_testes:
        veredito = dict(veredito, classificacao=PLAN_BUG, evidencias=(
            "(escalado: o teste foi reescrito e a falha se repetiu idêntica, então a origem está no plano de testes) "
            + veredito["evidencias"]))
        registrar_evento(raiz, {"tipo": "reparo_escalado", "de": "TEST_BUG", "para": PLAN_BUG})

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
        revisao = rodar_revisao(execucao, chat, raiz, arquivos, "codigo")
        if revisao is None:
            return False
        aprovada, relatorio = revisao
        aprovada = veto_valido(execucao, raiz, "codigo", aprovada, relatorio)
        tela.revisao("do código", aprovada, relatorio)
        execucao.registrar_revisao("codigo", aprovada)
        if not aprovada:
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


def implementar_e_reparar(execucao, chat, raiz):
    # O laço central: implementar, verificar e, se falhou, diagnosticar e reparar.
    mensagens = mensagens_implementacao(
        execucao.tarefa, execucao.spec, execucao.plano, texto_do_plano_de_testes(execucao))
    falhas_vistas = set()   # assinaturas das falhas já vistas nesta execução
    ultimo_veredito = None  # o diagnóstico mais recente (o das tentativas já gastas)
    tela.etapa("implementacao", "Implementação")

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

        # cada reparo registra em que etapa estava o erro e o que será feito (rastreabilidade)
        if veredito is not None:
            etapa, acao = ETAPA_E_ACAO[veredito["classificacao"]]
            registrar_evento(raiz, {"tipo": "reparo", "motivo": motivo, "culpado": veredito["classificacao"],
                                    "etapa": etapa, "acao": acao, "tentativa": execucao.tentativas + 1})

            if veredito["classificacao"] == PLAN_BUG:
                if not corrigir_plano_de_testes(execucao, chat, raiz, veredito, saida):
                    return

        try:
            avancar(execucao, raiz, REPAIRING)
        except TransicaoInvalida:
            # acabaram as tentativas de reparo
            culpa_do_teste = ultimo_veredito is not None and ultimo_veredito["classificacao"] in (TEST_BUG, PLAN_BUG)
            if motivo == "testes" and culpa_do_teste and descartar_testes_que_continuam_falhando(execucao, chat, raiz):
                avancar(execucao, raiz, DONE)
                return
            if execucao.estado != FAILED:
                avancar(execucao, raiz, FAILED)
            tela.aviso("as tentativas de reparo acabaram")
            return

        culpado, etapa_culpada, acao = None, None, None
        if veredito is not None:
            culpado = veredito["classificacao"]
            etapa_culpada, acao = ETAPA_E_ACAO[culpado]
        tela.reparo(execucao.tentativas, execucao.max_tentativas, MOTIVOS_DO_REPARO[motivo], culpado, etapa_culpada, acao)

        # O teste errado sai de cena para o modelo não copiá-lo de volta. Quem está errado decide o resto:
        #   TEST_BUG: o teste não seguiu o plano nem a spec -> o plano continua valendo
        #   PLAN_BUG: o teste seguiu um plano que contradiz a spec -> o plano já foi corrigido acima
        removidos = []
        if veredito is not None and veredito["classificacao"] in (TEST_BUG, PLAN_BUG):
            removidos = remover_testes_que_falharam(execucao, raiz)
            if removidos:
                registrar_evento(raiz, {"tipo": "testes_removidos", "testes": [nome for caminho, nome in removidos]})
                tela.aviso(f"o programa removeu o teste que falhou: {', '.join(nome for caminho, nome in removidos)}")

        mensagens = montar_mensagens_do_reparo(execucao, raiz, mensagens, saida, repetiu, motivo, veredito, removidos)
        avancar(execucao, raiz, IMPLEMENTING)


def rodar_agente(tarefa, raiz, chat, max_tentativas=3, max_iteracoes=40, revisar_spec=True, modo_debug=None,
                 diagnosticar=True, planejar_testes=True):
    raiz = Path(raiz).resolve()

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

    if not fazer_spec(execucao, chat, raiz):
        return finalizar(execucao, raiz)
    if not fazer_plano(execucao, chat, raiz):
        return finalizar(execucao, raiz)
    if planejar_testes and not fazer_plano_de_testes(execucao, chat, raiz):
        return finalizar(execucao, raiz)

    avancar(execucao, raiz, IMPLEMENTING)
    implementar_e_reparar(execucao, chat, raiz)
    return finalizar(execucao, raiz)

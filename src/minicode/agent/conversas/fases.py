import json
import time

from minicode.agent.gates.comandos import executar_comando
from minicode.agent.gates.escrita import (
    ESCRITAS, caminho_relativo, conteudo_atual, desescapar_conteudo, guardar_original, recusar_escrita,
)
from minicode.agent.maquina.estados import FAILED, FERRAMENTAS_POR_ESTADO, VERIFYING, TransicaoInvalida
from minicode.llm.esquema import esquema_acao, formato_da_resposta
from minicode.llm.parser import explicar_erro_json, extrair_acoes
from minicode.spec.documentos import extrair_documento
from minicode.tools.registry import FERRAMENTAS, PARAMETROS
from minicode.tracing.depuracao import depurar  # DEBUG
from minicode.tracing import tela
from minicode.tracing.registro import registrar_evento

LIMITE_REGISTRO = 300

# nas fases de spec e plano a LLM só pode explorar o projeto até este limite
MAX_LEITURAS = 4

# temperatura 0 faz o modelo repetir o mesmo padrão (loops). Documentos aceitam mais
# variação; a implementação emite JSON com código, então fica mais baixa.
TEMPERATURA_POR_FASE = {
    "spec": 0.6, "plan": 0.5, "implementacao": 0.3,
    "plano_de_testes": 0.3, "revisao_plano_de_testes": 0.2,
    "revisao": 0.2, "revisao_spec": 0.2, "diagnostico": 0.2,
}


# Cada fase é um loop de conversa com a LLM:
#   chama a LLM -> interpreta a resposta -> devolve um resultado ou um erro -> repete
# O resultado da ferramenta (ou o motivo do erro) volta para a LLM como mensagem do usuário.


def cortar_registro(texto):
    # textos longos não precisam ir inteiros para o actions.jsonl
    texto = str(texto)
    if len(texto) > LIMITE_REGISTRO:
        return texto[:LIMITE_REGISTRO] + "..."
    return texto


def avisar_llm(mensagens, texto):
    mensagens.append({"role": "user", "content": texto})


def pedir_resposta(execucao, chat, mensagens, raiz, fase, formato=None):
    # uma volta do loop: conta a iteração e chama a LLM. Devolve None se o limite estourou.
    # Com "formato" (um JSON Schema), o servidor só deixa a LLM gerar respostas nesse formato.
    execucao.contar_iteracao()
    if execucao.estado == FAILED:
        return None

    argumentos = {"temperature": TEMPERATURA_POR_FASE[fase]}
    if formato is not None:
        argumentos["response_format"] = formato

    depurar(execucao, raiz, "llm_pedido", fase=fase, iteracao=execucao.iteracoes,  # DEBUG
            temperatura=argumentos["temperature"],  # DEBUG
            schema=formato["json_schema"]["name"] if formato else None,  # DEBUG
            n_mensagens=len(mensagens),  # DEBUG
            caracteres=sum(len(m["content"]) for m in mensagens),  # DEBUG
            mensagens=mensagens)  # DEBUG

    tela.pensando(fase)
    inicio = time.perf_counter()
    try:
        resposta = chat(mensagens, **argumentos)
    except Exception as erro:
        # rede fora do ar, timeout, chave inválida...: a execução falha, mas com o erro registrado
        depurar(execucao, raiz, "llm_erro", fase=fase, erro=f"{type(erro).__name__}: {erro}")  # DEBUG
        registrar_evento(raiz, {"tipo": "erro_llm", "fase": fase, "erro": f"{type(erro).__name__}: {erro}"})
        tela.erro_llm(type(erro).__name__)
        execucao.mudar_para(FAILED)
        return None

    tela.pensou(time.perf_counter() - inicio)

    execucao.chamadas_llm += 1
    mensagens.append({"role": "assistant", "content": resposta})
    depurar(execucao, raiz, "llm_resposta", fase=fase, caracteres=len(resposta), resposta=resposta)  # DEBUG
    registrar_evento(raiz, {"tipo": "chamada_llm", "fase": fase, "resposta": cortar_registro(resposta)})
    return resposta


def executar_acao(execucao, raiz, acao):
    # roda a ferramenta pedida pela LLM, se o estado atual permitir. Devolve (ok, texto).
    nome = acao["tool"]
    args = acao["args"]
    tela.pensamento(acao.get("pensamento"))

    if acao.get("reparado"):
        registrar_evento(raiz, {"tipo": "json_reparado", "tool": nome})

    if not execucao.acao_permitida(nome):
        depurar(execucao, raiz, "ferramenta_negada", ferramenta=nome, args=args, motivo="não permitida no estado")  # DEBUG
        registrar_evento(raiz, {"tipo": "ferramenta_proibida", "tool": nome, "estado": execucao.estado})
        tela.negada(nome, args, "não permitida neste estado")
        return False, f"ERRO: a ferramenta {nome} não é permitida no estado {execucao.estado}"

    if nome in ESCRITAS:
        args = desescapar_conteudo(raiz, args)
        recusa = recusar_escrita(execucao, raiz, args)
        if recusa:
            motivo, evento, rotulo, mensagem = recusa
            depurar(execucao, raiz, "ferramenta_negada", ferramenta=nome, args=args, motivo=motivo)  # DEBUG
            registrar_evento(raiz, evento)
            tela.negada(nome, args, rotulo)
            return False, mensagem
        guardar_original(execucao, raiz, args)
        antes = conteudo_atual(raiz, args)

    try:
        if nome == "run_command":
            ok, texto = executar_comando(raiz, args)
        else:
            ok, texto = FERRAMENTAS[nome](raiz, **args)
    except TypeError:
        # a LLM mandou argumentos com nomes errados ou faltando
        ok, texto = False, f"ERRO: argumentos inválidos para {nome}"

    if nome in ESCRITAS and ok:
        execucao.registrar_escrita(args["path"])
        execucao.arquivos_vistos.add(caminho_relativo(raiz, args))   # quem grava o arquivo sabe o que ele contém
    elif nome == "read_file" and ok:
        execucao.arquivos_vistos.add(caminho_relativo(raiz, args))

    depurar(execucao, raiz, "ferramenta", ferramenta=nome, args=args, ok=ok, resultado=texto,  # DEBUG
            reparado=bool(acao.get("reparado")))  # DEBUG

    args_registro = {chave: cortar_registro(valor) for chave, valor in args.items()}
    registrar_evento(raiz, {
        "tipo": "ferramenta", "tool": nome, "args": args_registro,
        "ok": ok, "resultado": cortar_registro(texto),
    })
    if nome in ESCRITAS and ok:
        tela.escrita(nome, args["path"], antes, args["content"])
    else:
        tela.leitura(nome, args, ok, texto)
    return ok, texto


def rodar_fase_documento(execucao, chat, mensagens, raiz, tag, validar):
    # Fase de spec ou de plano. A LLM pode ler arquivos e termina entregando
    # o documento entre <tag> e </tag>. Devolve o documento, ou None se a execução falhou.
    leituras = 0
    chamadas_feitas = {}  # chamada -> resultado, para recusar repetições

    while True:
        resposta = pedir_resposta(execucao, chat, mensagens, raiz, tag)
        if resposta is None:
            return None

        documento = extrair_documento(resposta, tag)
        if documento is not None:
            ok, motivo = validar(documento)
            if ok:
                return documento
            registrar_evento(raiz, {"tipo": "documento_invalido", "fase": tag, "motivo": motivo})
            avisar_llm(mensagens, f"O documento é inválido: {motivo}\nEscreva de novo entre <{tag}> e </{tag}>.")
            continue

        acoes = extrair_acoes(resposta)
        if acoes:
            resultados = []

            # a resposta pode ter várias ações: executa todas, em ordem
            for acao in acoes:
                chamada = json.dumps([acao["tool"], acao["args"]], sort_keys=True)

                if chamada in chamadas_feitas:
                    # mesma ferramenta com os mesmos argumentos: não executa de novo
                    registrar_evento(raiz, {"tipo": "acao_repetida", "fase": tag, "tool": acao["tool"]})
                    resultados.append(f"Você já fez esta chamada ({acao['tool']}). O resultado foi:\n{chamadas_feitas[chamada]}\nNão repita. Escreva o documento entre <{tag}> e </{tag}>.")
                elif leituras >= MAX_LEITURAS:
                    registrar_evento(raiz, {"tipo": "limite_de_leituras", "fase": tag})
                    resultados.append(f"Limite de {MAX_LEITURAS} leituras atingido. Escreva agora o documento entre <{tag}> e </{tag}>.")
                else:
                    ok, texto = executar_acao(execucao, raiz, acao)
                    leituras += 1
                    chamadas_feitas[chamada] = texto
                    resultados.append(f"Resultado de {acao['tool']}:\n{texto}")

            avisar_llm(mensagens, "\n\n".join(resultados))
            continue

        # guarda a resposta inteira para depois entender por que o formato falhou
        motivo = explicar_erro_json(resposta)
        registrar_evento(raiz, {"tipo": "formato_invalido", "fase": tag, "motivo": motivo, "resposta_completa": resposta})
        avisar_llm(mensagens, f"Formato inválido: {motivo}. Responda com uma ação em JSON ou com o documento entre <{tag}> e </{tag}>.")


def rodar_fase_implementacao(execucao, chat, mensagens, raiz):
    # A LLM lê e escreve arquivos até pedir finish. Devolve True se o finish foi
    # aceito (estado vira VERIFYING), ou False se a execução falhou.

    # o schema só deixa a LLM pedir as ferramentas que este estado permite
    ferramentas_do_estado = FERRAMENTAS_POR_ESTADO[execucao.estado]
    formato = formato_da_resposta(esquema_acao(ferramentas_do_estado, PARAMETROS))

    while True:
        resposta = pedir_resposta(execucao, chat, mensagens, raiz, "implementacao", formato)
        if resposta is None:
            return False

        acoes = extrair_acoes(resposta)
        if not acoes:
            motivo = explicar_erro_json(resposta)
            registrar_evento(raiz, {"tipo": "formato_invalido", "fase": "implementacao", "motivo": motivo, "resposta_completa": resposta})
            avisar_llm(mensagens, f"Formato inválido: {motivo}. Responda apenas com ações em JSON.")
            continue

        resultados = []

        # a resposta pode ter várias ações: executa todas, em ordem
        for acao in acoes:
            if acao["tool"] == "finish":
                # quem decide se o finish vale é o gate da máquina de estados
                try:
                    execucao.mudar_para(VERIFYING)
                    registrar_evento(raiz, {"tipo": "finish_aceito"})
                    return True  # o que viesse depois do finish é ignorado
                except TransicaoInvalida as erro:
                    registrar_evento(raiz, {"tipo": "finish_recusado", "motivo": str(erro)})
                    resultados.append(f"finish recusado: {erro}")
            else:
                ok, texto = executar_acao(execucao, raiz, acao)
                resultados.append(f"Resultado de {acao['tool']}:\n{texto}")

        avisar_llm(mensagens, "\n\n".join(resultados))

import json

def validar_acao(acao):
    if isinstance(acao, dict) and "tool" in acao and "args" in acao:
        return True
    return False


def extrair_acao(texto):
    try:
        json_final = json.loads(texto)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    try:
        texto_limpo = texto.replace("```json", "").replace("```", "")
        json_final = json.loads(texto_limpo)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    try:
        inicio = texto.find("{")
        final = texto.rfind("}") + 1
        texto_limpo = texto[inicio:final]
        json_final = json.loads(texto_limpo)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    return None


def extrair_acoes(texto):
    # A LLM às vezes manda várias ações na mesma resposta, uma após a outra.
    # Devolve todas as ações válidas, na ordem em que aparecem (lista vazia se não houver).
    texto = texto.replace("```json", "").replace("```", "")
    decodificador = json.JSONDecoder()
    acoes = []
    posicao = 0
    quebrado = None  # onde começou um JSON quebrado que ainda não foi seguido por uma ação válida

    while True:
        inicio = texto.find("{", posicao)
        if inicio == -1:
            break

        try:
            # raw_decode lê um objeto JSON a partir de "inicio" e diz onde ele terminou
            objeto, fim = decodificador.raw_decode(texto, inicio)
        except json.JSONDecodeError:
            if quebrado is None:
                quebrado = inicio
            posicao = inicio + 1
            continue

        if validar_acao(objeto):
            acoes.append(objeto)
            quebrado = None  # o que veio antes era só lixo: uma ação válida veio depois
        posicao = fim

    # JSON quebrado no final da resposta: tenta consertar erros simples antes de desistir
    if quebrado is not None:
        acao = tentar_reparar(texto[quebrado:])
        if acao is not None:
            acoes.append(acao)

    return acoes


def reparar_json(trecho):
    # Conserta dois erros simples do modelo: faltar as aspas que fecham uma string
    # (logo antes das chaves finais) ou faltar chaves/colchetes no final.
    # Devolve o texto consertado, ou None se não for um desses casos.
    dentro_de_string = False
    escapado = False
    abertos = []

    for c in trecho:
        if escapado:
            escapado = False
        elif dentro_de_string:
            if c == "\\":
                escapado = True
            elif c == '"':
                dentro_de_string = False
        elif c == '"':
            dentro_de_string = True
        elif c in "{[":
            abertos.append(c)
        elif c in "}]" and abertos:
            abertos.pop()

    fechamentos = "".join("}" if a == "{" else "]" for a in reversed(abertos))

    if dentro_de_string:
        # as chaves finais ficaram "dentro" da string: tira, fecha a string e coloca de novo
        sem_fim = trecho.rstrip()
        if not sem_fim.endswith("}"):
            return None  # o texto parece cortado no meio: não adivinha o resto
        quantas = 0
        while sem_fim.endswith("}") and quantas < len(abertos):
            sem_fim = sem_fim[:-1]
            quantas += 1
        return sem_fim + '"' + fechamentos

    return trecho + fechamentos


def tentar_reparar(trecho):
    consertado = reparar_json(trecho.rstrip())
    if consertado is None:
        return None

    try:
        objeto = json.loads(consertado)
    except json.JSONDecodeError:
        return None

    if not validar_acao(objeto):
        return None

    objeto["reparado"] = True  # para o registro saber que o JSON foi consertado
    return objeto


def explicar_erro_json(texto):
    # diz à LLM o que está errado na resposta, para ela conseguir corrigir
    inicio = texto.find("{")
    if inicio == -1:
        return "não encontrei nenhum objeto JSON na resposta"

    try:
        json.JSONDecoder().raw_decode(texto, inicio)
    except json.JSONDecodeError as erro:
        return f"o JSON está inválido: {erro.msg} (linha {erro.lineno}, coluna {erro.colno})"

    return 'o JSON precisa ter as chaves "tool" e "args"'

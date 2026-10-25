import json

# Schema da resposta do revisor. Os "atendido" são booleanos: quem decide se foi aprovado
# é o programa (todos true), não uma frase do modelo.
ESQUEMA_REVISAO = {
    "type": "object",
    "properties": {
        "criterios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterio": {"type": "string"},
                    "atendido": {"type": "boolean"},
                    "motivo": {"type": "string"},
                },
                "required": ["criterio", "atendido", "motivo"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["criterios"],
    "additionalProperties": False,
}

# Na revisão do código, o revisor primeiro diz se o critério é sobre o CÓDIGO (comportamento,
# funções, erros) ou sobre os testes/processo. Critérios que não são sobre o código não podem
# ser verificados lendo o código, então não contam para reprovar (os testes cuidam deles).
ESQUEMA_REVISAO_CODIGO = {
    "type": "object",
    "properties": {
        "criterios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterio": {"type": "string"},
                    "sobre_o_codigo": {"type": "boolean"},
                    "atendido": {"type": "boolean"},
                    "motivo": {"type": "string"},
                },
                "required": ["criterio", "sobre_o_codigo", "atendido", "motivo"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["criterios"],
    "additionalProperties": False,
}

ESQUEMAS = {"codigo": ESQUEMA_REVISAO_CODIGO, "testes": ESQUEMA_REVISAO}

# Duas revisões, duas perguntas diferentes:
#   "codigo": o CÓDIGO cumpre cada critério?  (antes de rodar os testes)
#   "testes": os TESTES verificam cada critério, com o valor certo?  (depois que passam)

SISTEMA_REVISAO_CODIGO = """Você é um revisor de código rigoroso. Receberá uma especificação com critérios de aceitação e os arquivos de um projeto.

Para CADA critério de aceitação:
1. sobre_o_codigo: true se o critério descreve o comportamento do código (funções, retornos, erros, arquivos de código); false se ele fala dos testes ou do processo e não pode ser verificado lendo o código.
2. atendido: se sobre_o_codigo é true, decida se o CÓDIGO o atende, olhando o comportamento real: tipos de retorno, casos de borda, erros levantados e nomes de funções e arquivos citados.

O pedido original do usuário é a fonte da verdade; a especificação foi derivada dele. Se os dois divergirem (por exemplo no tipo de retorno), vale o pedido.

Não confie nos testes: eles podem estar fracos ou aceitar um comportamento errado. Marque atendido=false se o critério não for cumprido exatamente como está escrito, e explique em uma frase o que está diferente.

Responda somente com o JSON pedido, com todos os textos em português."""

SISTEMA_REVISAO_TESTES = """Você é um revisor de testes rigoroso. Receberá uma especificação com critérios de aceitação, o plano de testes (casos com entrada e resultado esperado, já conferidos) e os arquivos de um projeto, com o código e os testes.

Para CADA critério de aceitação, decida se existe pelo menos um TESTE que o verifica de verdade, seguindo os casos do plano de testes, e se o valor esperado desse teste está de acordo com o critério e com o plano (e não com o que o código por acaso faz).

Marque atendido=false se nenhum teste cobre o critério, ou se o teste espera um valor ou um tipo diferente do que o critério pede. Explique em uma frase o que falta ou está diferente.

Responda somente com o JSON pedido, com todos os textos em português."""

SISTEMAS = {"codigo": SISTEMA_REVISAO_CODIGO, "testes": SISTEMA_REVISAO_TESTES}

# Terceira revisão, anterior às outras duas: a ESPECIFICAÇÃO cumpre o PEDIDO do usuário?
# (as outras revisões comparam o código com a spec; se a spec já divergiu do pedido,
# todo o resto é construído sobre o erro)
ESQUEMA_REVISAO_SPEC = {
    "type": "object",
    "properties": {
        "requisitos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "requisito": {"type": "string"},
                    "coberto": {"type": "boolean"},
                    "motivo": {"type": "string"},
                },
                "required": ["requisito", "coberto", "motivo"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["requisitos"],
    "additionalProperties": False,
}

SISTEMA_REVISAO_SPEC = """Você é um revisor de especificações rigoroso. Receberá o PEDIDO original de um usuário e a ESPECIFICAÇÃO escrita a partir dele.

Liste cada requisito explícito do pedido (nomes de funções e de arquivos, parâmetros, tipos de retorno, erros a levantar, regras de negócio, restrições) e decida se a especificação o cumpre exatamente como foi pedido.

Marque coberto=false se a especificação omite, altera ou contradiz o requisito, e explique em uma frase o que está diferente. Requisitos que a especificação apenas detalha continuam cobertos.

Responda somente com o JSON pedido, com todos os textos em português."""


def mensagens_revisao_spec(tarefa, spec):
    usuario = f"Pedido do usuário:\n{tarefa}\n\nEspecificação:\n{spec}\n\nAvalie cada requisito do pedido."
    return [
        {"role": "system", "content": SISTEMA_REVISAO_SPEC},
        {"role": "user", "content": usuario},
    ]


def interpretar_revisao_spec(resposta):
    # Devolve (aprovada, relatorio), ou None se a resposta não puder ser interpretada.
    # Aprovada só se TODOS os requisitos vierem com coberto=true.
    try:
        requisitos = json.loads(resposta)["requisitos"]
        if not requisitos:
            return None

        linhas = []
        aprovada = True
        for r in requisitos:
            if r["coberto"] is not True:
                aprovada = False
            marca = "COBERTO" if r["coberto"] is True else "NÃO COBERTO"
            linhas.append(f"- [{marca}] {r['requisito']}: {r['motivo']}")
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None

    return aprovada, "\n".join(linhas)


def assinatura_da_reprovacao(relatorio):
    # Os critérios que o relatório reprovou (o começo de cada um basta para identificá-lo), para
    # saber se duas reprovações pedem a mesma coisa mesmo que o motivo venha com outras palavras.
    marca = "- [NÃO ATENDIDO] "
    return sorted(linha[len(marca):][:50] for linha in relatorio.splitlines() if linha.startswith(marca))


def mensagens_revisao(tipo, spec, arquivos, plano_de_testes=None, pedido=None):
    # o plano de testes só entra na revisão dos testes
    plano = f"Plano de testes:\n{plano_de_testes}\n\n" if plano_de_testes and tipo == "testes" else ""
    original = f"Pedido original do usuário:\n{pedido}\n\n" if pedido else ""
    usuario = f"{original}Especificação:\n{spec}\n\n{plano}Arquivos do projeto:\n{arquivos}\n\nAvalie cada critério de aceitação."
    return [
        {"role": "system", "content": SISTEMAS[tipo]},
        {"role": "user", "content": usuario},
    ]


def interpretar_revisao(resposta):
    # Devolve (aprovada, relatorio), ou None se a resposta não puder ser interpretada.
    # Aprovada só se TODOS os critérios vierem com atendido=true.
    try:
        criterios = json.loads(resposta)["criterios"]
        if not criterios:
            return None

        linhas = []
        aprovada = True
        for c in criterios:
            if c.get("sobre_o_codigo") is False:
                linhas.append(f"- [IGNORADO: não é sobre o código] {c['criterio']}: {c['motivo']}")
                continue
            if c["atendido"] is not True:
                aprovada = False
            marca = "ATENDIDO" if c["atendido"] is True else "NÃO ATENDIDO"
            linhas.append(f"- [{marca}] {c['criterio']}: {c['motivo']}")
    except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
        return None

    return aprovada, "\n".join(linhas)

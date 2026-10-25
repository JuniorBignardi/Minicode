import json


# O plano de testes é definido ANTES do código: para cada critério de aceitação da spec,
# casos com a entrada e o valor esperado. O schema só deixa citar critérios que existem de
# verdade na spec (enum), e o programa confere que nenhum critério ficou sem caso.

def criterios_da_spec(spec):
    # as linhas da seção "## Acceptance Criteria", sem o "- " do começo
    secao = spec.split("## Acceptance Criteria")[-1].split("\n## ")[0]
    criterios = []
    for linha in secao.splitlines():
        linha = linha.strip()
        if linha.startswith(("-", "*")):
            criterios.append(linha.lstrip("-* ").strip())
    return [c for c in criterios if c]


def esquema_plano_de_testes(criterios):
    return {
        "type": "object",
        "properties": {
            "casos": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterio": {"type": "string", "enum": criterios},
                        "entrada": {"type": "string"},
                        "esperado": {"type": "string"},
                    },
                    "required": ["criterio", "entrada", "esperado"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["casos"],
        "additionalProperties": False,
    }


SISTEMA_PLANO_DE_TESTES = """Você é um engenheiro de testes. Sua tarefa agora é definir os TESTES que vão verificar a especificação, ANTES de o código existir.

Para CADA critério de aceitação, escreva pelo menos um caso de teste com:
- criterio: o critério que o caso verifica, copiado exatamente;
- entrada: a chamada ou a situação que será testada, com valores concretos;
- esperado: o resultado exato esperado, ou o erro que deve ser levantado.

Verifique apenas o que a especificação define: não exija mensagens de erro, formatos ou detalhes que ela não menciona. Derive o valor esperado do critério, nunca de um código. Se o resultado envolver contas, escreva a conta junto com o valor (por exemplo "1 + 2 = 3"), refazendo-a passo a passo.

Cada caso precisa poder ser executado sozinho: se a entrada depende de dados ou arquivos, diga como criá-los dentro do próprio teste (no pytest, com a fixture tmp_path). Se o critério trata de uma regra entre várias, a entrada deve cumprir todas as outras regras, para o resultado esperado ser apenas o da regra testada.

Responda somente com o JSON pedido, com todos os textos em português."""


def mensagens_plano_de_testes(tarefa, spec, plano):
    usuario = f"Pedido do usuário:\n{tarefa}\n\nEspecificação:\n{spec}\n\nPlano:\n{plano}\n\nDefina os casos de teste."
    return [
        {"role": "system", "content": SISTEMA_PLANO_DE_TESTES},
        {"role": "user", "content": usuario},
    ]


def interpretar_plano_de_testes(resposta):
    # Devolve a lista de casos, ou None se a resposta não puder ser interpretada.
    try:
        casos = json.loads(resposta)["casos"]
        return [{"criterio": c["criterio"], "entrada": c["entrada"], "esperado": c["esperado"]} for c in casos]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def criterios_sem_caso(criterios, casos):
    # hard gate: critérios da spec que nenhum caso verifica
    cobertos = {c["criterio"] for c in casos}
    return [c for c in criterios if c not in cobertos]


def plano_de_testes_em_texto(casos):
    # o plano de testes como texto, para os prompts e para o .minicode/test_plan.md
    linhas = ["# Test Plan", ""]
    for numero, c in enumerate(casos, start=1):
        linhas.append(f"{numero}. Critério: {c['criterio']}")
        linhas.append(f"   - entrada: {c['entrada']}")
        linhas.append(f"   - esperado: {c['esperado']}")
    return "\n".join(linhas)


def validar_plano_de_testes(criterios, casos):
    # (True, "") ou (False, motivo) — o motivo volta para a LLM
    if not casos:
        return False, "o plano de testes não tem nenhum caso"

    faltando = criterios_sem_caso(criterios, casos)
    if faltando:
        lista = "\n".join(f"- {c}" for c in faltando)
        return False, f"estes critérios da especificação ficaram sem nenhum caso de teste:\n{lista}"

    return True, ""


# Revisão do plano de testes contra a spec: o valor esperado de cada caso está certo?
ESQUEMA_REVISAO_PLANO_DE_TESTES = {
    "type": "object",
    "properties": {
        "casos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "caso": {"type": "string"},
                    "esperado_correto": {"type": "boolean"},
                    "motivo": {"type": "string"},
                },
                "required": ["caso", "esperado_correto", "motivo"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["casos"],
    "additionalProperties": False,
}

SISTEMA_REVISAO_PLANO_DE_TESTES = """Você é um revisor de testes rigoroso. Receberá uma especificação e um plano de testes (casos com entrada e resultado esperado).

Para CADA caso, refaça você mesmo o cálculo ou o raciocínio a partir do critério e decida se o resultado esperado está correto. Marque esperado_correto=false se o resultado contradiz o critério, se uma conta está errada, se o caso exige algo que o critério não define (como o texto de uma mensagem de erro), ou se a entrada não cumpre as condições que o critério descreve.

Explique em uma frase o que está errado. Responda somente com o JSON pedido, com todos os textos em português."""


def mensagens_revisao_plano_de_testes(spec, casos):
    usuario = f"Especificação:\n{spec}\n\nPlano de testes:\n{plano_de_testes_em_texto(casos)}\n\nAvalie cada caso."
    return [
        {"role": "system", "content": SISTEMA_REVISAO_PLANO_DE_TESTES},
        {"role": "user", "content": usuario},
    ]


def interpretar_revisao_plano_de_testes(resposta):
    # Devolve (aprovada, relatorio), ou None se a resposta não puder ser interpretada.
    # Aprovada só se TODOS os casos vierem com esperado_correto=true.
    try:
        casos = json.loads(resposta)["casos"]
        if not casos:
            return None

        linhas = []
        aprovada = True
        for c in casos:
            if c["esperado_correto"] is not True:
                aprovada = False
            marca = "CORRETO" if c["esperado_correto"] is True else "ERRADO"
            linhas.append(f"- [{marca}] {c['caso']}: {c['motivo']}")
    except (json.JSONDecodeError, KeyError, TypeError):
        return None

    return aprovada, "\n".join(linhas)


def mensagem_correcao_do_plano_de_testes(motivo):
    return f"""O plano de testes tem um problema:

{motivo}

Escreva o plano de testes de novo, corrigindo isso e mantendo o que já estava correto."""

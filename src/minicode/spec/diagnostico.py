import json

# Classificações possíveis do diagnóstico de uma falha de teste
CODE_BUG = "CODE_BUG"                    # a implementação viola a especificação
TEST_BUG = "TEST_BUG"                    # o teste contradiz a especificação (ou não segue o plano de testes)
PLAN_BUG = "PLAN_BUG"                    # o teste segue o plano, mas o plano contradiz a especificação
ENVIRONMENT_ERROR = "ENVIRONMENT_ERROR"  # dependência, import ou configuração
UNKNOWN = "UNKNOWN"                      # evidências insuficientes
CLASSIFICACOES = [CODE_BUG, TEST_BUG, PLAN_BUG, ENVIRONMENT_ERROR, UNKNOWN]

# Tamanho mínimo (em caracteres) de uma citação da spec para valer como evidência
MIN_CITACAO = 12

# A classificação é forçada pelo schema (um enum): o diagnóstico não pode inventar categorias.
ESQUEMA_DIAGNOSTICO = {
    "type": "object",
    "properties": {
        "classificacao": {"type": "string", "enum": CLASSIFICACOES},
        "citacao_da_spec": {"type": "string"},
        "evidencias": {"type": "string"},
        "proxima_acao": {"type": "string"},
    },
    "required": ["classificacao", "citacao_da_spec", "evidencias", "proxima_acao"],
    "additionalProperties": False,
}

SISTEMA_DIAGNOSTICO = """Você é responsável por diagnosticar uma falha de testes em um projeto de software. Receberá a especificação, os arquivos do projeto (código e testes), a saída dos testes e, quando existir, o plano de testes (os casos com entrada e resultado esperado, derivados da especificação).

Antes de classificar:
0. O pedido original do usuário é a fonte da verdade; se a especificação divergir dele, vale o pedido.
1. Leia a especificação e seus critérios de aceitação.
2. Leia o teste que falhou e identifique o comportamento que ele espera.
3. Leia a implementação e rastreie o comportamento real.
4. Compare o que a especificação exige com o que o teste espera e com o que o código faz.
5. Use a saída dos testes como evidência.

Classifique a falha:
- CODE_BUG: a implementação viola a especificação.
- TEST_BUG: o teste contradiz a especificação ou não segue o plano de testes, verifica algo que a especificação não define, usa dados ou arquivos que ele mesmo não cria, ou tem uma forma de verificar incorreta.
- PLAN_BUG: o teste segue o plano de testes, e o plano contradiz a especificação (por exemplo, uma conta errada) ou exige algo que a especificação não define (por exemplo, o texto de uma mensagem de erro). Se o plano contém o valor ou a verificação que o teste usa e isso é o que está errado, a classificação é PLAN_BUG, não TEST_BUG. Só vale se existir um plano de testes.
- ENVIRONMENT_ERROR: a falha vem de dependência, import ou configuração do projeto, e não do código nem dos testes.
- UNKNOWN: as evidências não permitem decidir.

Em citacao_da_spec, copie EXATAMENTE, palavra por palavra, o trecho da especificação que sustenta a sua classificação. O trecho será conferido contra a especificação: se ele não existir nela, a classificação será descartada. Não parafraseie e não invente.

Você não altera nada: apenas diagnostica. Não afirme uma causa como confirmada quando houver só uma hipótese; nesse caso use UNKNOWN.

Responda somente com o JSON pedido, com todos os textos em português: classificacao, citacao_da_spec, evidencias (o que você observou) e proxima_acao (o que deve ser corrigido)."""


def mensagens_diagnostico(spec, arquivos, saida_testes, plano_de_testes=None, pedido=None):
    plano = f"Plano de testes:\n{plano_de_testes}\n\n" if plano_de_testes else ""
    original = f"Pedido original do usuário:\n{pedido}\n\n" if pedido else ""
    usuario = (
        f"{original}"
        f"Especificação:\n{spec}\n\n"
        f"{plano}"
        f"Arquivos do projeto:\n{arquivos}\n\n"
        f"Saída dos testes:\n{saida_testes}\n\n"
        "Diagnostique a falha."
    )
    return [
        {"role": "system", "content": SISTEMA_DIAGNOSTICO},
        {"role": "user", "content": usuario},
    ]


def interpretar_diagnostico(resposta):
    # Devolve o diagnóstico (dict) ou None se a resposta não puder ser interpretada.
    try:
        dados = json.loads(resposta)
        if dados["classificacao"] not in CLASSIFICACOES:
            return None
        return {
            "classificacao": dados["classificacao"],
            "citacao_da_spec": str(dados.get("citacao_da_spec", "")),
            "evidencias": str(dados["evidencias"]),
            "proxima_acao": str(dados["proxima_acao"]),
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def normalizar_texto(texto):
    # compara ignorando maiúsculas, espaços repetidos e marcas de formatação do markdown
    limpo = str(texto)
    for marca in "`*_":
        limpo = limpo.replace(marca, "")
    return " ".join(limpo.lower().split())


def citacao_encontrada(citacao, spec):
    # a citação precisa ser um trecho de verdade da spec (e não pequeno demais para provar algo)
    citacao = normalizar_texto(citacao).strip("\"' ")
    return len(citacao) >= MIN_CITACAO and citacao in normalizar_texto(spec)


def ancorar_na_spec(diagnostico, spec):
    # Hard gate de evidência: CODE_BUG, TEST_BUG e PLAN_BUG só valem se citarem a spec de verdade.
    # Devolve (diagnóstico, foi_rebaixado). Um diagnóstico sem prova vira UNKNOWN (sem restrição).
    if diagnostico["classificacao"] in (CODE_BUG, TEST_BUG, PLAN_BUG):
        if not citacao_encontrada(diagnostico["citacao_da_spec"], spec):
            rebaixado = dict(diagnostico)
            rebaixado["classificacao"] = UNKNOWN
            rebaixado["evidencias"] = (
                f"(rebaixado de {diagnostico['classificacao']}: a citação da especificação não foi encontrada na spec) "
                + diagnostico["evidencias"]
            )
            return rebaixado, True
    return diagnostico, False

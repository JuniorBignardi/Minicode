import json

import pytest

from minicode.agent.estados import (
    Execucao, TransicaoInvalida,
    SPECIFIED, PLANNED, IMPLEMENTING, VERIFYING, DIAGNOSING, REPAIRING, FAILED,
)
from minicode.spec.diagnostico import (
    CLASSIFICACOES, ESQUEMA_DIAGNOSTICO, ancorar_na_spec, citacao_encontrada,
    interpretar_diagnostico, mensagens_diagnostico,
)
from minicode.spec.revisao import interpretar_revisao_spec, mensagens_revisao_spec


def resposta(classificacao, evidencias="e", proxima="p", citacao="trecho da spec"):
    return json.dumps({"classificacao": classificacao, "citacao_da_spec": citacao,
                       "evidencias": evidencias, "proxima_acao": proxima})


# --- módulo do diagnóstico ---

@pytest.mark.parametrize("classificacao", CLASSIFICACOES)
def test_interpreta_cada_classificacao(classificacao):
    diag = interpretar_diagnostico(resposta(classificacao, "viu isto", "fazer aquilo", "um trecho"))
    assert diag == {"classificacao": classificacao, "citacao_da_spec": "um trecho",
                    "evidencias": "viu isto", "proxima_acao": "fazer aquilo"}


@pytest.mark.parametrize("bruta", [
    "",
    "não é json",
    "{}",
    resposta("OUTRA_COISA"),
    '{"classificacao": "TEST_BUG"}',
    "[1]",
])
def test_resposta_invalida_devolve_none(bruta):
    assert interpretar_diagnostico(bruta) is None


def test_o_schema_so_aceita_as_classificacoes_conhecidas():
    enum = ESQUEMA_DIAGNOSTICO["properties"]["classificacao"]["enum"]
    assert set(enum) == {"CODE_BUG", "TEST_BUG", "PLAN_BUG", "ENVIRONMENT_ERROR", "UNKNOWN"}
    assert set(ESQUEMA_DIAGNOSTICO["required"]) == {"classificacao", "citacao_da_spec", "evidencias", "proxima_acao"}


# --- evidência verificável: a citação precisa existir na spec ---

SPEC_DE_EXEMPLO = """# Specification

## Acceptance Criteria
- A função `soma(a, b)` devolve a soma dos dois números.
- A função levanta ValueError se algum argumento for negativo.
"""


def diag(classificacao, citacao):
    return {"classificacao": classificacao, "citacao_da_spec": citacao, "evidencias": "ev", "proxima_acao": "p"}


def test_citacao_literal_da_spec_e_aceita():
    assert citacao_encontrada("devolve a soma dos dois números", SPEC_DE_EXEMPLO) is True


def test_citacao_ignora_maiusculas_espacos_e_marcas_de_markdown():
    assert citacao_encontrada("A FUNÇÃO  soma(a, b)\ndevolve a SOMA dos dois", SPEC_DE_EXEMPLO) is True


@pytest.mark.parametrize("citacao", [
    "",
    "soma",                                                  # curta demais para provar algo
    "a função deve devolver apenas o primeiro erro",          # inventada
    "levanta TypeError se algum argumento for negativo",     # quase, mas diferente
])
def test_citacao_inventada_ou_curta_nao_vale(citacao):
    assert citacao_encontrada(citacao, SPEC_DE_EXEMPLO) is False


def test_diagnostico_sem_citacao_valida_e_rebaixado_para_unknown():
    original = diag("TEST_BUG", "a spec exige que devolva só o primeiro erro")
    novo, rebaixado = ancorar_na_spec(original, SPEC_DE_EXEMPLO)
    assert rebaixado is True
    assert novo["classificacao"] == "UNKNOWN"
    assert "rebaixado de TEST_BUG" in novo["evidencias"]
    assert original["classificacao"] == "TEST_BUG"           # o original não é alterado


@pytest.mark.parametrize("classificacao", ["CODE_BUG", "TEST_BUG"])
def test_diagnostico_com_citacao_valida_e_mantido(classificacao):
    original = diag(classificacao, "devolve a soma dos dois números")
    novo, rebaixado = ancorar_na_spec(original, SPEC_DE_EXEMPLO)
    assert rebaixado is False and novo == original


@pytest.mark.parametrize("classificacao", ["UNKNOWN", "ENVIRONMENT_ERROR"])
def test_unknown_e_ambiente_nao_precisam_de_citacao(classificacao):
    original = diag(classificacao, "")
    novo, rebaixado = ancorar_na_spec(original, SPEC_DE_EXEMPLO)
    assert rebaixado is False and novo["classificacao"] == classificacao


def test_o_diagnostico_recebe_spec_arquivos_e_saida_dos_testes():
    mensagens = mensagens_diagnostico("SPEC AQUI", "--- a.py\ncodigo", "saida do pytest")
    usuario = mensagens[1]["content"]
    assert "SPEC AQUI" in usuario and "--- a.py" in usuario and "saida do pytest" in usuario
    assert [m["role"] for m in mensagens] == ["system", "user"]
    assert "CODE_BUG" in mensagens[0]["content"] and "TEST_BUG" in mensagens[0]["content"]


# --- gates do estado DIAGNOSING ---

def execucao_verificando():
    e = Execucao("t")
    e.spec, e.plano = "s", "p"
    e.mudar_para(SPECIFIED)
    e.mudar_para(PLANNED)
    e.mudar_para(IMPLEMENTING)
    e.registrar_escrita("a.py")
    e.mudar_para(VERIFYING)
    return e


def test_verifying_pode_ir_para_diagnosing_se_os_testes_falharam():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.mudar_para(DIAGNOSING)
    assert e.estado == DIAGNOSING


def test_nao_diagnostica_se_os_testes_passaram():
    e = execucao_verificando()
    e.registrar_testes(True)
    with pytest.raises(TransicaoInvalida, match="não há falha"):
        e.mudar_para(DIAGNOSING)


def test_diagnosing_so_vai_para_repairing_com_diagnostico():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.mudar_para(DIAGNOSING)
    with pytest.raises(TransicaoInvalida, match="sem diagnóstico"):
        e.mudar_para(REPAIRING)

    e.registrar_diagnostico({"classificacao": "UNKNOWN", "evidencias": "", "proxima_acao": ""})
    e.mudar_para(REPAIRING)
    assert e.estado == REPAIRING
    assert e.tentativas == 1


def test_diagnosing_nao_pode_ir_direto_para_implementing_nem_done():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.mudar_para(DIAGNOSING)
    for destino in (IMPLEMENTING, "DONE"):
        with pytest.raises(TransicaoInvalida):
            e.mudar_para(destino)


def test_diagnosing_pode_falhar():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.mudar_para(DIAGNOSING)
    e.mudar_para(FAILED)
    assert e.estado == FAILED


def test_o_diagnostico_define_a_restricao_de_escrita():
    e = Execucao("t")

    e.registrar_diagnostico({"classificacao": "TEST_BUG", "evidencias": "", "proxima_acao": ""})
    assert e.restricao_escrita == "testes"

    e.registrar_diagnostico({"classificacao": "CODE_BUG", "evidencias": "", "proxima_acao": ""})
    assert e.restricao_escrita == "codigo"

    for classificacao in ("UNKNOWN", "ENVIRONMENT_ERROR"):
        e.registrar_diagnostico({"classificacao": classificacao, "evidencias": "", "proxima_acao": ""})
        assert e.restricao_escrita is None


def test_depois_de_duas_recusas_a_restricao_e_levantada():
    e = Execucao("t")
    e.registrar_diagnostico({"classificacao": "TEST_BUG", "evidencias": "", "proxima_acao": ""})

    assert e.pode_recusar() is True
    assert e.pode_recusar() is True
    assert e.restricao_escrita == "testes"
    assert e.pode_recusar() is False          # a 3ª recusa levanta a restrição
    assert e.restricao_escrita is None


def test_as_recusas_voltam_a_zero_a_cada_reparo():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.recusas_do_reparo = 2
    e.mudar_para(REPAIRING)
    assert e.recusas_do_reparo == 0


def test_restringir_false_ignora_a_classificacao():
    e = Execucao("t")
    e.registrar_diagnostico({"classificacao": "TEST_BUG", "evidencias": "", "proxima_acao": ""}, restringir=False)
    assert e.restricao_escrita is None
    assert e.diagnostico["classificacao"] == "TEST_BUG"


def test_diagnostico_e_restricao_valem_so_ate_o_proximo_verifying():
    e = execucao_verificando()
    e.registrar_testes(False)
    e.mudar_para(DIAGNOSING)
    e.registrar_diagnostico({"classificacao": "TEST_BUG", "evidencias": "", "proxima_acao": ""})
    e.mudar_para(REPAIRING)
    e.mudar_para(IMPLEMENTING)
    assert e.restricao_escrita == "testes"       # vale durante o reparo

    e.registrar_escrita("tests/test_a.py")
    e.mudar_para(VERIFYING)
    assert e.diagnostico is None and e.restricao_escrita is None


# --- revisão da spec contra o pedido ---

def resposta_spec(*itens):
    return json.dumps({"requisitos": [{"requisito": r, "coberto": c, "motivo": m} for r, c, m in itens]})


def test_spec_aprovada_quando_todos_os_requisitos_estao_cobertos():
    aprovada, relatorio = interpretar_revisao_spec(resposta_spec(("a", True, "ok"), ("b", True, "ok")))
    assert aprovada is True and "NÃO COBERTO" not in relatorio


def test_spec_reprovada_lista_o_que_nao_foi_coberto():
    aprovada, relatorio = interpretar_revisao_spec(resposta_spec(("devolve lista", False, "a spec diz string"), ("erro", True, "ok")))
    assert aprovada is False
    assert "[NÃO COBERTO] devolve lista: a spec diz string" in relatorio


@pytest.mark.parametrize("bruta", ["", "lixo", "{}", '{"requisitos": []}', '{"requisitos": [{"requisito": "a"}]}'])
def test_revisao_da_spec_invalida_devolve_none(bruta):
    assert interpretar_revisao_spec(bruta) is None


def test_a_revisao_da_spec_recebe_o_pedido_e_a_spec():
    mensagens = mensagens_revisao_spec("PEDIDO DO USUARIO", "SPEC ESCRITA")
    usuario = mensagens[1]["content"]
    assert "PEDIDO DO USUARIO" in usuario and "SPEC ESCRITA" in usuario

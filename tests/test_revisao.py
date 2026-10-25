import json

import pytest

from minicode.spec.revisao import interpretar_revisao, mensagens_revisao


def resposta(*criterios):
    return json.dumps({"criterios": [
        {"criterio": c, "atendido": ok, "motivo": m} for c, ok, m in criterios
    ]})


def test_todos_atendidos_aprova():
    aprovada, relatorio = interpretar_revisao(resposta(("a", True, "ok"), ("b", True, "ok")))
    assert aprovada is True
    assert "NÃO ATENDIDO" not in relatorio


def test_um_nao_atendido_reprova_e_aparece_no_relatorio():
    aprovada, relatorio = interpretar_revisao(resposta(
        ("devolve lista", False, "devolve texto"),
        ("erro se o arquivo não existe", True, "levanta FileNotFoundError"),
    ))
    assert aprovada is False
    assert "[NÃO ATENDIDO] devolve lista: devolve texto" in relatorio
    assert "[ATENDIDO] erro se o arquivo não existe" in relatorio


def test_so_true_de_verdade_conta_como_atendido():
    # um "sim" em texto não é um booleano: a revisão só aprova com true
    bruta = json.dumps({"criterios": [{"criterio": "a", "atendido": "sim", "motivo": "ok"}]})
    aprovada, relatorio = interpretar_revisao(bruta)
    assert aprovada is False


@pytest.mark.parametrize("bruta", [
    "",
    "não é json",
    "{}",
    '{"criterios": []}',
    '{"criterios": [{"criterio": "a"}]}',
    '{"criterios": "texto"}',
    "[1, 2]",
])
def test_resposta_que_nao_da_para_interpretar_devolve_none(bruta):
    assert interpretar_revisao(bruta) is None


def test_as_duas_revisoes_fazem_perguntas_diferentes():
    codigo = mensagens_revisao("codigo", "spec", "arquivos")
    testes = mensagens_revisao("testes", "spec", "arquivos")
    assert "o CÓDIGO o atende" in codigo[0]["content"]
    assert "TESTE que o verifica" in testes[0]["content"]
    assert codigo[0]["content"] != testes[0]["content"]


def test_a_revisao_recebe_a_spec_e_os_arquivos():
    mensagens = mensagens_revisao("codigo", "## Acceptance Criteria\n- fatorial(5) == 120", "--- fat.py\ndef fatorial(n): ...")
    usuario = mensagens[1]["content"]
    assert "fatorial(5) == 120" in usuario
    assert "def fatorial(n)" in usuario
    assert [m["role"] for m in mensagens] == ["system", "user"]


def test_o_pedido_original_chega_aos_juizes():
    from minicode.spec.diagnostico import mensagens_diagnostico
    from minicode.spec.revisao import mensagens_revisao
    pedido = "devolva a lista ordenada das palavras"

    assert pedido in mensagens_revisao("codigo", "spec", "arquivos", pedido=pedido)[1]["content"]
    assert pedido in mensagens_revisao("testes", "spec", "arquivos", pedido=pedido)[1]["content"]
    assert pedido in mensagens_diagnostico("spec", "arquivos", "saída", pedido=pedido)[1]["content"]


def test_sem_pedido_a_mensagem_continua_igual():
    from minicode.spec.revisao import mensagens_revisao
    assert "Pedido original" not in mensagens_revisao("codigo", "spec", "arquivos")[1]["content"]

from minicode.spec.prompts import (
    mensagem_reparo, mensagens_implementacao, mensagens_plano, mensagens_recomeco, mensagens_spec,
)


def test_o_prompt_da_spec_nao_cita_casos_de_nenhuma_tarefa():
    sistema = mensagens_spec("tarefa")[0]["content"].lower()
    for caso in ["fatorial", "carrinho", "tmp_path", "pytest.raises", "contar_linhas", "keyerror"]:
        assert caso not in sistema


def test_mensagens_de_cada_fase_tem_system_e_user():
    for mensagens in [
        mensagens_spec("tarefa"),
        mensagens_plano("tarefa", "spec"),
        mensagens_implementacao("tarefa", "spec", "plano"),
    ]:
        assert [m["role"] for m in mensagens] == ["system", "user"]


def test_prompt_de_implementacao_exige_testes_novos_e_protege_os_existentes():
    sistema = mensagens_implementacao("tarefa", "spec", "plano")[0]["content"]
    assert "NOVO" in sistema
    assert "não podem ser alterados" in sistema


def test_mensagem_de_reparo_traz_a_saida_e_lembra_que_o_teste_pode_estar_errado():
    texto = mensagem_reparo("assert 1 == 2")
    assert "assert 1 == 2" in texto
    assert "nos testes que você mesmo escreveu" in texto


def test_mensagem_de_reparo_com_spec_pede_diagnostico_teste_ou_codigo():
    spec = "## Acceptance Criteria\n- fatorial(5) == 120"
    texto = mensagem_reparo("assert 1 == 2", spec=spec)
    assert "fatorial(5) == 120" in texto
    assert "CONTRADIZ a especificação" in texto
    assert "erro está no TESTE" in texto and "erro está no CÓDIGO" in texto


def test_mensagem_de_reparo_sem_spec_nao_tem_diagnostico():
    assert "CONTRADIZ" not in mensagem_reparo("erro")


def test_reparo_avisa_que_o_codigo_foi_aprovado_pela_revisao():
    com = mensagem_reparo("erro", codigo_aprovado=True)
    assert "APROVOU o código" in com
    assert "estar nos TESTES" in com
    assert "APROVOU" not in mensagem_reparo("erro")


def test_recomeco_tambem_leva_o_aviso_do_codigo_aprovado():
    mensagens = mensagens_recomeco("t", "s", "p", "arquivos", "erro", codigo_aprovado=True)
    assert "APROVOU o código" in mensagens[1]["content"]


def test_mensagem_de_reparo_avisa_quando_o_resultado_se_repetiu():
    assert "IDÊNTICO" not in mensagem_reparo("erro")
    assert "IDÊNTICO" in mensagem_reparo("erro", repetiu=True)


def test_mensagens_de_recomeco_tem_so_o_essencial():
    mensagens = mensagens_recomeco("tarefa", "spec", "plano", "--- a.py\nx = 1", "assert 1 == 2", repetiu=True)
    assert [m["role"] for m in mensagens] == ["system", "user"]
    usuario = mensagens[1]["content"]
    assert "tarefa" in usuario and "spec" in usuario and "plano" in usuario
    assert "Estado atual dos arquivos" in usuario and "x = 1" in usuario
    assert "assert 1 == 2" in usuario
    assert "IDÊNTICO" in usuario


def test_mensagem_de_reparo_diz_que_o_sistema_roda_os_testes():
    texto = mensagem_reparo("erro")
    assert "O sistema roda os testes sozinho" in texto or "o sistema roda os testes sozinho" in texto
    assert "não precisa rodá-los" in texto and "run_command" in texto


def test_regra_geral_de_testar_so_o_que_a_spec_define():
    sistema = mensagens_implementacao("tarefa", "spec", "plano")[0]["content"]
    assert "Teste apenas o que a especificação define" in sistema


def test_os_prompts_pedem_que_o_teste_crie_seus_arquivos_e_isole_a_regra():
    from minicode.spec.plano_de_testes import SISTEMA_PLANO_DE_TESTES
    assert "tmp_path" in mensagens_implementacao("t", "s", "p")[0]["content"]
    assert "tmp_path" in SISTEMA_PLANO_DE_TESTES
    assert "cumprir todas as outras regras" in SISTEMA_PLANO_DE_TESTES


def test_o_reinicio_mostra_o_diff_do_que_mudou_nos_arquivos_que_ja_existiam():
    from minicode.spec.prompts import mensagens_recomeco
    diff = "--- precos.py (original)\n+++ precos.py (atual)\n-    return 110.0\n+    return 100.1"

    usuario = mensagens_recomeco("tarefa", "spec", "plano", "--- precos.py\nx", "saída", mudancas=diff)[1]["content"]

    assert "diff contra o original" in usuario and "-    return 110.0" in usuario


def test_sem_mudancas_o_reinicio_nao_tem_o_bloco_de_diff():
    from minicode.spec.prompts import mensagens_recomeco
    usuario = mensagens_recomeco("tarefa", "spec", "plano", "--- a.py\nx = 1", "saída")[1]["content"]
    assert "diff contra o original" not in usuario

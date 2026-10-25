import pytest

from minicode.agent.estados import (
    Execucao, TransicaoInvalida,
    RECEIVED, SPECIFIED, PLANNED, IMPLEMENTING, VERIFYING, REPAIRING, DONE, FAILED,
)


def execucao_em(estado):
    # monta uma execução já no estado pedido, passando pelo caminho válido
    e = Execucao("tarefa")
    caminho = [SPECIFIED, PLANNED, IMPLEMENTING, VERIFYING]
    e.spec = "spec"
    e.plano = "plano"
    for destino in caminho:
        if e.estado == estado:
            break
        if destino == VERIFYING:
            e.registrar_escrita("a.py")
        e.mudar_para(destino)
    return e


def test_caminho_feliz():
    e = Execucao("tarefa")
    e.spec = "spec"
    e.mudar_para(SPECIFIED)
    e.plano = "plano"
    e.mudar_para(PLANNED)
    e.mudar_para(IMPLEMENTING)
    e.registrar_escrita("a.py")
    e.mudar_para(VERIFYING)
    e.registrar_testes(True)
    e.mudar_para(DONE)
    assert e.estado == DONE


@pytest.mark.parametrize("de, para", [
    (RECEIVED, IMPLEMENTING),
    (RECEIVED, DONE),
    (SPECIFIED, IMPLEMENTING),
    (PLANNED, VERIFYING),
    (IMPLEMENTING, DONE),
])
def test_transicoes_fora_da_tabela_sao_proibidas(de, para):
    e = execucao_em(de)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(para)


def test_sem_spec_nao_vai_para_specified():
    e = Execucao("tarefa")
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(SPECIFIED)


def test_sem_plano_nao_vai_para_planned():
    e = Execucao("tarefa")
    e.spec = "spec"
    e.mudar_para(SPECIFIED)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(PLANNED)


def test_finish_sem_escrita_nao_vai_para_verifying():
    e = execucao_em(IMPLEMENTING)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(VERIFYING)


def test_arquivo_citado_na_tarefa_precisa_existir_no_caminho_certo(tmp_path):
    e = execucao_em(IMPLEMENTING)
    e.raiz = tmp_path
    e.arquivos_exigidos = ["fat.py"]

    (tmp_path / "pasta").mkdir()
    (tmp_path / "pasta" / "fat.py").write_text("x", encoding="utf-8")
    e.registrar_escrita("pasta/fat.py")
    with pytest.raises(TransicaoInvalida, match="fat.py"):
        e.mudar_para(VERIFYING)

    (tmp_path / "fat.py").write_text("x", encoding="utf-8")
    e.mudar_para(VERIFYING)
    assert e.estado == VERIFYING


def test_sem_arquivo_citado_o_gate_nao_exige_nada(tmp_path):
    e = execucao_em(IMPLEMENTING)
    e.raiz = tmp_path
    e.registrar_escrita("qualquer.py")
    e.mudar_para(VERIFYING)
    assert e.estado == VERIFYING


# --- revisões contra a especificação ---

def execucao_verificando_com_revisao():
    e = execucao_em(VERIFYING)
    e.exige_revisao = True
    e.registrar_testes(True)
    return e


def test_com_revisao_exigida_done_precisa_das_duas_aprovadas():
    e = execucao_verificando_com_revisao()
    with pytest.raises(TransicaoInvalida, match="revisões"):
        e.mudar_para(DONE)

    e.registrar_revisao("codigo", True)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(DONE)       # falta a revisão dos testes

    e.registrar_revisao("testes", True)
    e.mudar_para(DONE)
    assert e.estado == DONE


def test_uma_revisao_reprovada_impede_done():
    e = execucao_verificando_com_revisao()
    e.registrar_revisao("codigo", True)
    e.registrar_revisao("testes", False)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(DONE)


def test_sem_revisao_exigida_done_continua_so_com_os_testes():
    e = execucao_em(VERIFYING)
    e.registrar_testes(True)
    e.mudar_para(DONE)
    assert e.estado == DONE


def test_revisao_reprovada_permite_reparar_mesmo_com_os_testes_passando():
    e = execucao_verificando_com_revisao()
    e.registrar_revisao("testes", False)
    e.mudar_para(REPAIRING)
    assert e.estado == REPAIRING
    assert e.tentativas == 1


def test_testes_passando_e_revisoes_ok_nao_ha_o_que_reparar():
    e = execucao_verificando_com_revisao()
    e.registrar_revisao("codigo", True)
    e.registrar_revisao("testes", True)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(REPAIRING)


def test_escrever_invalida_as_revisoes_anteriores():
    e = execucao_verificando_com_revisao()
    e.registrar_revisao("codigo", True)
    e.registrar_revisao("testes", True)
    e.registrar_escrita("b.py")
    assert e.revisoes == {"codigo": None, "testes": None}


def test_testes_falhando_nao_chegam_a_done():
    e = execucao_em(VERIFYING)
    e.registrar_testes(False)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(DONE)


def test_escrever_depois_dos_testes_invalida_o_resultado():
    e = execucao_em(VERIFYING)
    e.registrar_testes(True)
    e.registrar_escrita("b.py")
    assert e.testes_passaram is False


def test_repair_conta_tentativas_e_respeita_o_limite():
    e = execucao_em(VERIFYING)
    for _ in range(3):
        e.registrar_testes(False)
        e.mudar_para(REPAIRING)
        e.mudar_para(IMPLEMENTING)
        e.registrar_escrita("a.py")
        e.mudar_para(VERIFYING)
    e.registrar_testes(False)
    assert e.tentativas == 3
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(REPAIRING)
    e.mudar_para(FAILED)
    assert e.estado == FAILED


def test_nao_repara_se_os_testes_passaram():
    e = execucao_em(VERIFYING)
    e.registrar_testes(True)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(REPAIRING)


def test_estados_finais_nao_saem():
    e = execucao_em(VERIFYING)
    e.registrar_testes(True)
    e.mudar_para(DONE)
    with pytest.raises(TransicaoInvalida):
        e.mudar_para(IMPLEMENTING)


def test_limite_de_iteracoes_leva_a_failed():
    e = Execucao("tarefa", max_iteracoes=3)
    for _ in range(3):
        e.contar_iteracao()
    assert e.estado == RECEIVED
    e.contar_iteracao()
    assert e.estado == FAILED


def test_escrita_so_e_permitida_em_implementing():
    assert execucao_em(RECEIVED).acao_permitida("write_file") is False
    assert execucao_em(PLANNED).acao_permitida("write_file") is False
    assert execucao_em(IMPLEMENTING).acao_permitida("write_file") is True


def test_leitura_e_permitida_nas_fases_iniciais():
    assert execucao_em(RECEIVED).acao_permitida("read_file") is True
    assert execucao_em(SPECIFIED).acao_permitida("list_files") is True


def test_finish_so_em_implementing():
    assert execucao_em(PLANNED).acao_permitida("finish") is False
    assert execucao_em(IMPLEMENTING).acao_permitida("finish") is True

import json

import pytest

from minicode.agent.estados import Execucao, IMPLEMENTING, PLANNED, SPECIFIED, TEST_PLANNED, TransicaoInvalida
from minicode.agent.revisoes import MAX_CORRECOES_DO_PLANO_DE_TESTES, rodar_plano_de_testes
from minicode.spec.plano_de_testes import (
    criterios_da_spec, criterios_sem_caso, esquema_plano_de_testes, interpretar_plano_de_testes,
    interpretar_revisao_plano_de_testes, plano_de_testes_em_texto, validar_plano_de_testes,
)
from minicode.spec.prompts import mensagens_implementacao
from minicode.spec.revisao import interpretar_revisao, mensagens_revisao
from minicode.tracing.registro import iniciar_registro

SPEC = """# Specification

## Objective
Criar a função fatorial.

## Acceptance Criteria
- fatorial(0) == 1
- fatorial(5) == 120

## Notes
- isto não é critério
"""

CRITERIOS = ["fatorial(0) == 1", "fatorial(5) == 120"]


def rodar(a_execucao, chat, raiz, tarefa, plano):
    iniciar_registro(raiz, tarefa)   # os eventos precisam de uma pasta .minicode
    return rodar_plano_de_testes(a_execucao, chat, raiz, tarefa, plano)


def caso(criterio, entrada="fatorial(0)", esperado="1"):
    return {"criterio": criterio, "entrada": entrada, "esperado": esperado}


def resposta_do_plano(casos):
    return json.dumps({"casos": casos})


def revisao_do_plano(aprovada, motivo="ok"):
    return json.dumps({"casos": [{"caso": "x", "esperado_correto": aprovada, "motivo": motivo}]})


# --- o módulo ---

def test_criterios_da_spec_le_so_a_secao_de_criterios():
    assert criterios_da_spec(SPEC) == CRITERIOS


def test_o_schema_so_aceita_criterios_que_existem_na_spec():
    esquema = esquema_plano_de_testes(CRITERIOS)
    assert esquema["properties"]["casos"]["items"]["properties"]["criterio"]["enum"] == CRITERIOS


def test_criterio_sem_nenhum_caso_e_apontado():
    casos = [caso(CRITERIOS[0])]
    assert criterios_sem_caso(CRITERIOS, casos) == [CRITERIOS[1]]

    valido, motivo = validar_plano_de_testes(CRITERIOS, casos)
    assert valido is False and CRITERIOS[1] in motivo


def test_plano_completo_e_valido_e_plano_vazio_nao():
    assert validar_plano_de_testes(CRITERIOS, [caso(c) for c in CRITERIOS]) == (True, "")
    assert validar_plano_de_testes(CRITERIOS, [])[0] is False


def test_interpretar_plano_de_testes_com_resposta_ruim_devolve_none():
    assert interpretar_plano_de_testes("não é json") is None
    assert interpretar_plano_de_testes('{"casos": "texto"}') is None
    assert interpretar_plano_de_testes(resposta_do_plano([caso("a")])) == [caso("a")]


def test_plano_em_texto_lista_criterio_entrada_e_esperado():
    texto = plano_de_testes_em_texto([caso("fatorial(5) == 120", "fatorial(5)", "120")])
    assert "fatorial(5) == 120" in texto and "entrada: fatorial(5)" in texto and "esperado: 120" in texto


def test_revisao_do_plano_so_aprova_se_todos_os_casos_estiverem_certos():
    assert interpretar_revisao_plano_de_testes(revisao_do_plano(True))[0] is True
    aprovada, relatorio = interpretar_revisao_plano_de_testes(revisao_do_plano(False, "10*2+20*3 é 80"))
    assert aprovada is False and "ERRADO" in relatorio and "80" in relatorio
    assert interpretar_revisao_plano_de_testes("lixo") is None


# --- a fase ---

def execucao_com_spec():
    execucao = Execucao("crie fatorial")
    execucao.spec = SPEC
    execucao.exige_revisao = True
    return execucao


def chat_do_plano(respostas):
    fila = list(respostas)
    chamadas = []

    def chat(mensagens, temperature=0, **kw):
        chamadas.append(kw["response_format"]["json_schema"]["name"])
        return fila.pop(0)

    return chat, chamadas


def casos_completos():
    return [caso(c) for c in CRITERIOS]


def test_plano_completo_e_aprovado_na_primeira(tmp_path):
    chat, chamadas = chat_do_plano([resposta_do_plano(casos_completos()), revisao_do_plano(True)])

    casos = rodar(execucao_com_spec(), chat, tmp_path, "crie fatorial", "1. criar")

    assert casos == casos_completos()
    assert chamadas == ["plano_de_testes", "revisao_plano_de_testes"]


def test_criterio_sem_caso_volta_para_a_llm_corrigir(tmp_path):
    incompleto = resposta_do_plano([caso(CRITERIOS[0])])
    chat, chamadas = chat_do_plano([incompleto, resposta_do_plano(casos_completos()), revisao_do_plano(True)])

    casos = rodar(execucao_com_spec(), chat, tmp_path, "crie fatorial", "1. criar")

    assert casos == casos_completos()
    assert chamadas == ["plano_de_testes", "plano_de_testes", "revisao_plano_de_testes"]   # o incompleto nem foi revisado


def test_valor_esperado_errado_reprovado_pela_revisao_volta_para_a_llm(tmp_path):
    chat, chamadas = chat_do_plano([
        resposta_do_plano(casos_completos()), revisao_do_plano(False, "fatorial(5) é 120"),
        resposta_do_plano(casos_completos()), revisao_do_plano(True),
    ])

    casos = rodar(execucao_com_spec(), chat, tmp_path, "crie fatorial", "1. criar")

    assert casos == casos_completos()
    assert chamadas.count("plano_de_testes") == 2


def test_depois_das_correcoes_segue_com_a_ultima_versao(tmp_path):
    rodadas = MAX_CORRECOES_DO_PLANO_DE_TESTES + 1
    chat, chamadas = chat_do_plano([resposta_do_plano(casos_completos()), revisao_do_plano(False, "errado")] * rodadas)

    casos = rodar(execucao_com_spec(), chat, tmp_path, "crie fatorial", "1. criar")

    assert casos == casos_completos()
    assert chamadas.count("plano_de_testes") == rodadas
    eventos = (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8")
    assert "plano_de_testes_reprovado_seguindo" in eventos


def test_sem_revisao_ligada_o_plano_nao_e_revisado(tmp_path):
    execucao = execucao_com_spec()
    execucao.exige_revisao = False
    chat, chamadas = chat_do_plano([resposta_do_plano(casos_completos())])

    assert rodar(execucao, chat, tmp_path, "crie fatorial", "1. criar") == casos_completos()
    assert chamadas == ["plano_de_testes"]


# --- o estado ---

def execucao_planejada():
    execucao = Execucao("tarefa")
    execucao.spec, execucao.plano = "spec", "plano"
    execucao.mudar_para(SPECIFIED)
    execucao.mudar_para(PLANNED)
    return execucao


def test_sem_plano_de_testes_nao_vai_para_test_planned():
    with pytest.raises(TransicaoInvalida):
        execucao_planejada().mudar_para(TEST_PLANNED)


def test_com_plano_de_testes_o_caminho_passa_por_test_planned():
    execucao = execucao_planejada()
    execucao.plano_de_testes = [caso("a")]
    execucao.mudar_para(TEST_PLANNED)
    execucao.mudar_para(IMPLEMENTING)
    assert execucao.estado == IMPLEMENTING


def test_o_estado_test_planned_nao_permite_ferramentas():
    execucao = execucao_planejada()
    execucao.plano_de_testes = [caso("a")]
    execucao.mudar_para(TEST_PLANNED)
    assert execucao.acao_permitida("read_file") is False


def test_sem_plano_de_testes_o_caminho_antigo_continua_valido():
    execucao = execucao_planejada()
    execucao.mudar_para(IMPLEMENTING)
    assert execucao.estado == IMPLEMENTING


# --- onde o plano de testes é usado ---

def test_o_prompt_de_implementacao_inclui_o_plano_de_testes():
    mensagens = mensagens_implementacao("tarefa", "spec", "plano", "# Test Plan\n1. Critério: x")
    assert "Plano de testes" in mensagens[1]["content"] and "Critério: x" in mensagens[1]["content"]
    assert "Plano de testes" not in mensagens_implementacao("tarefa", "spec", "plano")[1]["content"]


def test_so_a_revisao_dos_testes_recebe_o_plano_de_testes():
    assert "Plano de testes" in mensagens_revisao("testes", "spec", "arquivos", "# Test Plan")[1]["content"]
    assert "Plano de testes" not in mensagens_revisao("codigo", "spec", "arquivos", "# Test Plan")[1]["content"]


# --- revisão do código ignora critério que não é sobre o código ---

def revisao_do_codigo(*criterios):
    return json.dumps({"criterios": [
        {"criterio": c, "sobre_o_codigo": sobre, "atendido": atendido, "motivo": "m"} for c, sobre, atendido in criterios
    ]})


def test_criterio_sobre_testes_nao_reprova_a_revisao_do_codigo():
    resposta = revisao_do_codigo(("fatorial(5) == 120", True, True), ("os testes devem passar", False, False))

    aprovada, relatorio = interpretar_revisao(resposta)

    assert aprovada is True
    assert "IGNORADO" in relatorio and "os testes devem passar" in relatorio


def test_criterio_sobre_o_codigo_nao_atendido_continua_reprovando():
    resposta = revisao_do_codigo(("fatorial(5) == 120", True, False), ("os testes devem passar", False, False))
    assert interpretar_revisao(resposta)[0] is False


def test_revisao_antiga_sem_o_campo_sobre_o_codigo_continua_valida():
    resposta = json.dumps({"criterios": [{"criterio": "x", "atendido": False, "motivo": "m"}]})
    assert interpretar_revisao(resposta)[0] is False


def test_a_volta_para_test_planned_exige_um_diagnostico():
    from minicode.agent.estados import DIAGNOSING, REPAIRING
    execucao = execucao_planejada()
    execucao.plano_de_testes = [caso("a")]
    execucao.mudar_para(TEST_PLANNED)
    execucao.mudar_para(IMPLEMENTING)
    execucao.arquivos_alterados = ["a.py"]
    execucao.mudar_para(__import__("minicode.agent.estados", fromlist=["VERIFYING"]).VERIFYING)
    execucao.mudar_para(DIAGNOSING)

    with pytest.raises(TransicaoInvalida):
        execucao.mudar_para(TEST_PLANNED)   # sem diagnóstico não volta

    execucao.registrar_diagnostico({"classificacao": "PLAN_BUG"})
    execucao.mudar_para(TEST_PLANNED)
    execucao.mudar_para(REPAIRING)
    assert execucao.estado == REPAIRING and execucao.tentativas == 1

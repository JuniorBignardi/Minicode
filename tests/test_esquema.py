from minicode.agent.estados import FERRAMENTAS_POR_ESTADO, IMPLEMENTING, RECEIVED
from minicode.llm.esquema import esquema_acao, formato_da_resposta
from minicode.tools.registry import PARAMETROS


def test_o_enum_tem_so_as_ferramentas_pedidas():
    esquema = esquema_acao(["read_file", "finish"], PARAMETROS)
    assert esquema["properties"]["tool"]["enum"] == ["read_file", "finish"]


def test_os_tres_campos_sao_obrigatorios_e_nada_alem_deles():
    esquema = esquema_acao(["finish"], PARAMETROS)
    assert esquema["required"] == ["pensamento", "tool", "args"]
    assert esquema["additionalProperties"] is False
    assert esquema["properties"]["args"]["additionalProperties"] is False


def test_os_argumentos_vem_das_ferramentas_permitidas():
    esquema = esquema_acao(["read_file"], PARAMETROS)
    assert set(esquema["properties"]["args"]["properties"]) == {"path"}

    esquema = esquema_acao(["write_file", "list_files"], PARAMETROS)
    assert set(esquema["properties"]["args"]["properties"]) == {"path", "content", "diretorio"}


def test_o_estado_de_implementacao_permite_escrever_e_terminar():
    esquema = esquema_acao(FERRAMENTAS_POR_ESTADO[IMPLEMENTING], PARAMETROS)
    enum = esquema["properties"]["tool"]["enum"]
    assert "write_file" in enum and "finish" in enum
    assert "run_tests" not in enum


def test_um_estado_sem_escrita_nao_tem_write_file_no_schema():
    esquema = esquema_acao(FERRAMENTAS_POR_ESTADO[RECEIVED], PARAMETROS)
    enum = esquema["properties"]["tool"]["enum"]
    assert "write_file" not in enum and "finish" not in enum


def test_formato_no_padrao_da_api_da_openai():
    formato = formato_da_resposta({"type": "object"})
    assert formato == {"type": "json_schema", "json_schema": {"name": "acao", "schema": {"type": "object"}}}

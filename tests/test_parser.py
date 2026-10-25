import pytest
from minicode.llm.parser import explicar_erro_json, extrair_acao, extrair_acoes

ACAO = {"tool": "read_file", "args": {"path": "a.py"}}
JSON = '{"tool": "read_file", "args": {"path": "a.py"}}'


# --- casos que devem funcionar ---

def test_json_puro():
    assert extrair_acao(JSON) == ACAO

def test_json_com_espacos_e_quebras_de_linha():
    assert extrair_acao("\n  " + JSON + "  \n") == ACAO

def test_bloco_markdown_com_json():
    assert extrair_acao("```json\n" + JSON + "\n```") == ACAO

def test_bloco_markdown_sem_a_palavra_json():
    assert extrair_acao("```\n" + JSON + "\n```") == ACAO

def test_texto_antes_do_json():
    assert extrair_acao("Vou ler o arquivo: " + JSON) == ACAO

def test_texto_antes_e_depois_com_bloco():
    texto = "Claro!\n```json\n" + JSON + "\n```\nMe avise o resultado."
    assert extrair_acao(texto) == ACAO

def test_json_com_args_aninhados():
    texto = '{"tool": "write_file", "args": {"path": "a.py", "content": "x = {1: 2}"}}'
    assert extrair_acao(texto)["args"]["content"] == "x = {1: 2}"


# --- casos que devem ser recusados (devolver None) ---

@pytest.mark.parametrize("texto", [
    "",
    "   ",
    "só texto, sem JSON nenhum",
    "{json quebrado",
    '{"tool": "read_file", "args": ',      # JSON cortado no meio
    "[1, 2, 3]",                           # JSON válido, mas não é uma ação
    "42",
])
def test_entradas_invalidas_devolvem_none(texto):
    assert extrair_acao(texto) is None

# --- extrair_acoes (várias ações na mesma resposta) ---

A1 = '{"tool": "write_file", "args": {"path": "a.py", "content": "x = 1\\n"}}'
A2 = '{"tool": "write_file", "args": {"path": "b.py", "content": "y = 2\\n"}}'


def test_acoes_uma_so():
    assert extrair_acoes(JSON) == [ACAO]


def test_acoes_duas_em_linhas_separadas():
    acoes = extrair_acoes(A1 + "\n" + A2)
    assert [a["args"]["path"] for a in acoes] == ["a.py", "b.py"]


def test_acoes_com_texto_e_markdown_no_meio():
    texto = "Vou criar:\n```json\n" + A1 + "\n```\ne depois:\n```json\n" + A2 + "\n```\nPronto."
    acoes = extrair_acoes(texto)
    assert [a["args"]["path"] for a in acoes] == ["a.py", "b.py"]


def test_acoes_conteudo_com_chaves_nao_confunde():
    acao = '{"tool": "write_file", "args": {"path": "a.py", "content": "d = {1: 2}\\n"}}'
    assert extrair_acoes(acao + "\n" + A2)[0]["args"]["content"] == "d = {1: 2}\n"


def test_acoes_ignora_json_que_nao_e_acao():
    assert extrair_acoes('{"a": 1}\n' + JSON) == [ACAO]


def test_acoes_json_quebrado_no_inicio_nao_impede_a_proxima():
    assert extrair_acoes('{"tool": "x", "args": \n' + A2) == [extrair_acao(A2)]


@pytest.mark.parametrize("texto", ["", "só texto", "[1, 2]", "42", "{'tool': 'x', 'args': {}}"])
def test_acoes_sem_acao_devolve_lista_vazia(texto):
    assert extrair_acoes(texto) == []


# --- conserto de JSON com erros simples ---

def test_conserta_aspas_de_fechamento_que_faltam():
    # o mesmo erro que o modelo cometeu: faltou o " antes das chaves finais
    texto = '{"tool": "write_file", "args": {"path": "a.py", "content": "def f():\\n    print(\'oi\')"}}'
    texto = texto.replace("\')\"}}", "\')}}")
    acoes = extrair_acoes(texto)
    assert len(acoes) == 1
    assert acoes[0]["args"]["content"] == "def f():\n    print('oi')"
    assert acoes[0]["reparado"] is True


def test_conserta_chaves_finais_que_faltam():
    acoes = extrair_acoes('{"tool": "finish", "args": {}')
    assert acoes == [{"tool": "finish", "args": {}, "reparado": True}]


def test_conserta_so_o_ultimo_objeto_quando_o_primeiro_esta_certo():
    quebrado = '{"tool": "write_file", "args": {"path": "b.py", "content": "y = 2}}'
    acoes = extrair_acoes(A1 + "\n" + quebrado)
    assert [a["args"]["path"] for a in acoes] == ["a.py", "b.py"]
    assert "reparado" not in acoes[0]
    assert acoes[1]["reparado"] is True


def test_nao_conserta_texto_cortado_no_meio_do_conteudo():
    # sem chaves finais, o código está incompleto: gravar daria um arquivo pela metade
    assert extrair_acoes('{"tool": "write_file", "args": {"path": "a.py", "content": "def f():\\n    ret') == []


def test_nao_conserta_o_que_continua_invalido():
    assert extrair_acoes('{"tool": "x", "args": {"a": 1,') == []


def test_explicar_erro_json():
    assert "nenhum objeto JSON" in explicar_erro_json("só conversa")
    assert "Unterminated string" in explicar_erro_json('{"tool": "x", "args": {"a": "oi}}')
    assert 'chaves "tool" e "args"' in explicar_erro_json('{"a": 1}')


def test_acao_sem_args_devolve_none():
    assert extrair_acao('{"tool": "read_file"}') is None


def test_dicionario_sem_tool_devolve_none():
    assert extrair_acao('{"a": 1}') is None


def test_aspas_simples_nao_sao_json():
    assert extrair_acao("{'tool': 'read_file', 'args': {}}") is None

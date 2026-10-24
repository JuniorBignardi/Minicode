import pytest
from minicode.llm.parser import extrair_acao

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

def test_aspas_simples_nao_sao_json():
    assert extrair_acao("{'tool': 'read_file', 'args': {}}") is None

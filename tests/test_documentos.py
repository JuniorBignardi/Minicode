import pytest

from minicode.spec.documentos import arquivos_citados, extrair_documento, validar_spec, validar_plano

SPEC_VALIDA = """# Specification

## Objective
Criar uma função fatorial.

## Acceptance Criteria
- fatorial(5) == 120
- fatorial(0) == 1
"""


# --- extrair_documento ---

def test_extrai_conteudo_entre_tags():
    assert extrair_documento("<spec>conteudo</spec>", "spec") == "conteudo"


def test_extrai_ignorando_texto_em_volta():
    texto = "Aqui está a spec:\n<spec>\nlinha 1\nlinha 2\n</spec>\nEspero ter ajudado."
    assert extrair_documento(texto, "spec") == "linha 1\nlinha 2"


def test_extrai_o_primeiro_se_houver_dois():
    texto = "<spec>primeiro</spec> e <spec>segundo</spec>"
    assert extrair_documento(texto, "spec") == "primeiro"


@pytest.mark.parametrize("texto", [
    "",
    "texto sem tag nenhuma",
    "<spec>sem fechar",
    "sem abrir</spec>",
    "<plan>é outro documento</plan>",
])
def test_sem_documento_devolve_none(texto):
    assert extrair_documento(texto, "spec") is None


def test_tag_pedida_define_o_que_e_extraido():
    texto = "<spec>a spec</spec><plan>o plano</plan>"
    assert extrair_documento(texto, "plan") == "o plano"


# --- arquivos_citados ---

@pytest.mark.parametrize("texto, esperado", [
    ("Crie fatorial no arquivo fatorial.py.", ["fatorial.py"]),
    ("Na função saudacao de saudacao.py, adicione um parâmetro", ["saudacao.py"]),
    ("Refatore area.py e atualize src/util.py", ["area.py", "src/util.py"]),
    ("Edite fat.py e depois fat.py de novo", ["fat.py"]),
    ("Crie uma função fatorial(n), sem citar arquivo", []),
    ("Veja o README.md", []),
])
def test_arquivos_citados(texto, esperado):
    assert arquivos_citados(texto) == esperado


# --- validar_spec ---

def test_spec_valida():
    ok, motivo = validar_spec(SPEC_VALIDA)
    assert ok is True


def test_spec_com_criterios_numerados_e_valida():
    spec = "## Objective\nX\n\n## Acceptance Criteria\n1. a\n2. b\n"
    assert validar_spec(spec)[0] is True


@pytest.mark.parametrize("spec", [
    "",
    "## Acceptance Criteria\n- a\n- b\n",                          # sem Objective
    "## Objective\nX\n",                                           # sem Acceptance Criteria
    "## Objective\nX\n\n## Acceptance Criteria\n- só um\n",        # 1 critério
    "## Objective\nX\n\n## Acceptance Criteria\nnenhum critério\n",  # 0 critérios
])
def test_spec_invalida_e_explica_o_motivo(spec):
    ok, motivo = validar_spec(spec)
    assert ok is False
    assert motivo != ""


def test_so_conta_criterios_da_secao_certa():
    spec = (
        "## Objective\n- item solto\n- outro\n\n"
        "## Acceptance Criteria\n- só um\n\n"
        "## Notes\n- nota 1\n- nota 2\n"
    )
    assert validar_spec(spec)[0] is False


# --- validar_plano ---

@pytest.mark.parametrize("plano", [
    "1. ler o arquivo\n2. escrever a função",
    "- ler o arquivo\n- escrever a função",
])
def test_plano_valido(plano):
    assert validar_plano(plano)[0] is True


@pytest.mark.parametrize("plano", [
    "",
    "1. um passo só",
    "vou fazer tudo de uma vez, sem lista",
])
def test_plano_invalido_e_explica_o_motivo(plano):
    ok, motivo = validar_plano(plano)
    assert ok is False
    assert motivo != ""

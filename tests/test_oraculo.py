import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments" / "gabarito"))

import oraculo  # noqa: E402

TESTE_CERTO = "from fatorial import fatorial\n\ndef test_cinco():\n    assert fatorial(5) == 120\n"
TESTE_ERRADO = "from fatorial import fatorial\n\ndef test_cinco():\n    assert fatorial(5) == 100\n"
FATORIAL_CERTO = oraculo.REFERENCIAS_FACEIS[1]["fatorial.py"]
FATORIAL_ERRADO = "def fatorial(n):\n    return n\n"


def caso(entrada, esperado):
    return {"criterio": "c", "entrada": entrada, "esperado": esperado}


def test_caso_com_valor_certo_errado_e_excecao():
    avaliacoes = oraculo.avaliar_casos("facil", 1, [
        caso("fatorial(5)", "120"),
        caso("fatorial(5)", "100"),
        caso("fatorial(-1)", "ValueError"),
        caso("fatorial(-1)", "0"),
    ])
    assert avaliacoes == ["correto", "errado", "correto", "errado"]


def test_entrada_que_a_referencia_nao_executa_e_inavaliavel():
    assert oraculo.avaliar_casos("facil", 1, [caso("funcao_que_nao_existe(1)", "1")]) == ["inavaliavel"]


def test_lista_booleano_e_texto():
    avaliacoes = oraculo.avaliar_casos("facil", 2, [caso("eh_palindromo('Arara')", "True"), caso("eh_palindromo('python')", "True")])
    assert avaliacoes == ["correto", "errado"]

    avaliacoes = oraculo.avaliar_casos("facil", 8, [caso("saudacao('Ana', formal=True)", "Prezado(a) Ana"),
                                                      caso("saudacao('Ana')", "'Olá, Ana'")])
    assert avaliacoes == ["correto", "correto"]

    assert oraculo.avaliar_casos("facil", 4, [caso("contar_palavras('a b a')", "{'a': 2, 'b': 1}")]) == ["correto"]


def test_varios_comandos_terminando_em_uma_expressao():
    entrada = "c = Carrinho(); c.adicionar('a', 10, 2); c.total()"
    assert oraculo.avaliar_casos("dificil", 3, [caso(entrada, "20"), caso(entrada, "10")]) == ["correto", "errado"]


def test_float_compara_com_tolerancia_e_int_nao_vira_texto():
    assert oraculo.iguais(3.0, 3.0000000001) is True
    assert oraculo.iguais(1, True) is False
    assert oraculo.iguais([1], [1]) is True


def montar_snapshot(tmp_path, codigo, teste):
    (tmp_path / "tests").mkdir()
    (tmp_path / "fatorial.py").write_text(codigo, encoding="utf-8")
    (tmp_path / "tests" / "test_f.py").write_text(teste, encoding="utf-8")
    return tmp_path


def test_teste_errado_e_codigo_certo_o_oraculo_aponta_o_teste(tmp_path):
    assert oraculo.veredito_do_oraculo("facil", 1, montar_snapshot(tmp_path, FATORIAL_CERTO, TESTE_ERRADO)) == "TEST_BUG"


def test_codigo_errado_e_teste_certo_o_oraculo_aponta_o_codigo(tmp_path):
    assert oraculo.veredito_do_oraculo("facil", 1, montar_snapshot(tmp_path, FATORIAL_ERRADO, TESTE_CERTO)) == "CODE_BUG"


def test_sem_falha_e_tarefa_de_criar_testes(tmp_path):
    assert oraculo.veredito_do_oraculo("facil", 1, montar_snapshot(tmp_path, FATORIAL_CERTO, TESTE_CERTO)) == "sem_falha"
    assert oraculo.veredito_do_oraculo("facil", 10, tmp_path) == "nao_aplicavel"


def test_testes_do_agente_que_falham_na_referencia_sao_testes_errados(tmp_path):
    montar_snapshot(tmp_path, FATORIAL_ERRADO, TESTE_ERRADO)
    assert oraculo.testes_errados_do_agente("facil", 1, tmp_path, ["tests/test_f.py"])
    (tmp_path / "tests" / "test_f.py").write_text(TESTE_CERTO, encoding="utf-8")
    assert oraculo.testes_errados_do_agente("facil", 1, tmp_path, ["tests/test_f.py"]) == set()


def test_varias_entradas_em_um_processo_so_cada_uma_com_o_seu_espaco(tmp_path):
    (tmp_path / "carrinho.py").write_text(oraculo.REFERENCIAS_DIFICEIS[3]["carrinho.py"], encoding="utf-8")
    saidas = oraculo.executar_entradas(tmp_path, [
        "c = Carrinho(); c.adicionar('a', 10, 2); c.total()",
        "c = Carrinho(); c.total()",
        "Carrinho().remover('x')",
        "nome_que_nao_existe",
    ])
    assert saidas == [{"ok": True, "repr": "20"}, {"ok": True, "repr": "0"}, {"ok": False, "excecao": "KeyError"},
                      {"ok": False, "excecao": "NameError"}]

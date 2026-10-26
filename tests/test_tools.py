from minicode.tools.files import create_file, list_files, read_file, write_file
from minicode.tools.testes import nomes_dos_testes_que_falharam, run_tests
from minicode.tools.registry import FERRAMENTAS


def test_write_e_read(tmp_path):
    ok, texto = write_file(tmp_path, "src/a.py", "x = 1\ny = 2\n")
    assert ok is True

    ok, conteudo = read_file(tmp_path, "src/a.py")
    assert ok is True
    assert conteudo == "x = 1\ny = 2\n"


def test_read_arquivo_inexistente(tmp_path):
    ok, texto = read_file(tmp_path, "nao_existe.py")
    assert ok is False
    assert "ERRO" in texto


def test_caminho_fora_do_projeto_nao_le_nem_escreve(tmp_path):
    ok, texto = read_file(tmp_path, "../segredo.txt")
    assert ok is False

    ok, texto = write_file(tmp_path, "../fora.txt", "oi")
    assert ok is False
    assert not (tmp_path.parent / "fora.txt").exists()


def test_list_files_ignora_pastas_internas(tmp_path):
    write_file(tmp_path, "a.py", "")
    write_file(tmp_path, "src/b.py", "")
    write_file(tmp_path, ".minicode/state.json", "{}")
    write_file(tmp_path, "__pycache__/c.pyc", "")

    ok, texto = list_files(tmp_path)
    assert ok is True
    assert texto.splitlines() == ["a.py", "src/b.py"]


def test_list_files_em_pasta_inexistente(tmp_path):
    ok, texto = list_files(tmp_path, "nao_existe")
    assert ok is False


def test_run_tests_passando(tmp_path):
    write_file(tmp_path, "test_ok.py", "def test_ok():\n    assert 1 + 1 == 2\n")
    passou, saida = run_tests(tmp_path)
    assert passou is True


def test_run_tests_falhando(tmp_path):
    write_file(tmp_path, "test_ruim.py", "def test_ruim():\n    assert 1 + 1 == 3\n")
    passou, saida = run_tests(tmp_path)
    assert passou is False
    assert "assert" in saida


def test_run_tests_devolve_os_acentos_sem_corromper(tmp_path):
    write_file(tmp_path, "test_acento.py", 'def test_acento():\n    assert "maçã e coração" == "banana"\n')
    passou, saida = run_tests(tmp_path)
    assert passou is False
    assert "maçã e coração" in saida
    assert "Ã" not in saida


def test_run_tests_sem_nenhum_teste_nao_conta_como_passou(tmp_path):
    passou, saida = run_tests(tmp_path)
    assert passou is False


def test_registry_tem_as_ferramentas():
    assert set(FERRAMENTAS) == {"list_files", "read_file", "search_code", "git_diff", "create_file", "write_file", "run_tests"}


def test_nomes_dos_testes_que_falharam():
    saida = (
        "=== FAILURES ===\n"
        "_______ test_primeiro _______\n\ncorpo\n"
        "_______ test_com_parametro[1-2] _______\n\ncorpo\n"
        "_______ TestCarrinho.test_dentro_de_classe _______\n\ncorpo\n"
        "_______ ERROR collecting tests/test_x.py _______\n"
    )
    assert nomes_dos_testes_que_falharam(saida) == ["test_primeiro", "test_com_parametro", "test_dentro_de_classe"]


def test_nomes_dos_testes_que_falharam_sem_falhas():
    assert nomes_dos_testes_que_falharam("2 passed in 0.01s") == []


# --- create_file ---

def test_create_file_cria_um_arquivo_novo_com_as_pastas(tmp_path):
    ok, texto = create_file(tmp_path, "pasta/novo.py", "x = 1")
    assert ok is True
    assert read_file(tmp_path, "pasta/novo.py")[1] == "x = 1"


def test_create_file_recusa_arquivo_que_ja_existe_e_nao_o_altera(tmp_path):
    write_file(tmp_path, "a.py", "x = 1")
    ok, texto = create_file(tmp_path, "a.py", "x = 2")
    assert ok is False and "write_file" in texto
    assert read_file(tmp_path, "a.py")[1] == "x = 1"


def test_create_file_recusa_caminho_fora_do_projeto(tmp_path):
    ok, texto = create_file(tmp_path, "../fora.py", "x = 1")
    assert ok is False and "fora do projeto" in texto


# --- o código escrito pela LLM não enxerga os segredos do ambiente ---

def test_os_testes_nao_recebem_a_chave_da_api(tmp_path, monkeypatch):
    from minicode.tools.testes import run_tests
    monkeypatch.setenv("MINICODE_API_KEY", "segredo-do-professor")
    (tmp_path / "test_ambiente.py").write_text(
        "import os\n\ndef test_sem_chave():\n    assert 'MINICODE_API_KEY' not in os.environ\n"
        "    assert 'segredo-do-professor' not in str(os.environ)\n", encoding="utf-8")

    passou, saida = run_tests(tmp_path)

    assert passou is True, saida


def test_os_testes_continuam_rodando_com_o_ambiente_reduzido(tmp_path):
    from minicode.tools.testes import run_tests
    (tmp_path / "test_ok.py").write_text("def test_ok(tmp_path):\n    assert tmp_path.exists()\n", encoding="utf-8")
    assert run_tests(tmp_path)[0] is True

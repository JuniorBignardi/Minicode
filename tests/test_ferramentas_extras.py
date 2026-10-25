import subprocess

from minicode.tools.busca import search_code
from minicode.tools.git import git_diff


# --- search_code ---

def test_search_code_acha_o_trecho_com_arquivo_e_linha(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\ndef Soma(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("y = 2\n", encoding="utf-8")

    ok, texto = search_code(tmp_path, "soma")

    assert ok is True and texto == "a.py:2: def Soma(a, b):"


def test_search_code_sem_resultado_nao_e_erro(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    ok, texto = search_code(tmp_path, "nada")
    assert ok is True and "nenhum resultado" in texto


def test_search_code_ignora_pastas_internas_e_binarios(tmp_path):
    (tmp_path / ".minicode").mkdir()
    (tmp_path / ".minicode" / "log.txt").write_text("segredo\n", encoding="utf-8")
    (tmp_path / "dado.bin").write_bytes(b"\xff\xfe segredo")

    ok, texto = search_code(tmp_path, "segredo")

    assert "nenhum resultado" in texto


def test_search_code_recusa_padrao_vazio_e_pasta_fora_do_projeto(tmp_path):
    assert search_code(tmp_path, "")[0] is False
    ok, texto = search_code(tmp_path, "x", "../fora")
    assert ok is False and "fora do projeto" in texto


# --- git_diff ---

def test_git_diff_fora_de_um_repositorio_devolve_erro(tmp_path):
    ok, texto = git_diff(tmp_path)
    assert ok is False and "repositório" in texto


def test_git_diff_mostra_o_que_mudou(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init")
    git("config", "user.email", "t@t.com")
    git("config", "user.name", "t")
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "inicio")
    assert git_diff(tmp_path) == (True, "nenhuma alteração desde o último commit")

    (tmp_path / "a.py").write_text("x = 2\n", encoding="utf-8")
    ok, texto = git_diff(tmp_path)

    assert ok is True and "-x = 1" in texto and "+x = 2" in texto

from minicode.safety.protegidos import listar_testes


def criar(raiz, caminho):
    arquivo = raiz / caminho
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_text("", encoding="utf-8")


def test_lista_so_arquivos_de_teste(tmp_path):
    for caminho in ["tests/test_a.py", "test_b.py", "c_test.py", "conftest.py",
                    "tests/helper.py", "src/app.py", "README.md"]:
        criar(tmp_path, caminho)

    assert listar_testes(tmp_path) == [
        "c_test.py", "conftest.py", "test_b.py", "tests/helper.py", "tests/test_a.py",
    ]


def test_ignora_pastas_que_nao_sao_do_projeto(tmp_path):
    criar(tmp_path, ".venv/lib/test_z.py")
    criar(tmp_path, "__pycache__/test_y.py")
    criar(tmp_path, "test_ok.py")

    assert listar_testes(tmp_path) == ["test_ok.py"]


def test_projeto_sem_testes(tmp_path):
    criar(tmp_path, "src/app.py")
    assert listar_testes(tmp_path) == []

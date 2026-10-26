import pytest

from minicode.safety.caminhos import validar_caminho
from minicode.safety.comandos import validar_comando


def test_caminho_dentro_do_projeto(tmp_path):
    alvo = validar_caminho(tmp_path, "src/app.py")
    assert alvo == (tmp_path / "src" / "app.py").resolve()


@pytest.mark.parametrize("caminho", [
    "../fora.txt",
    "src/../../fora.txt",
    "/etc/passwd",
    "C:\\Windows\\system.ini",
])
def test_caminho_fora_do_projeto_e_recusado(tmp_path, caminho):
    with pytest.raises(ValueError):
        validar_caminho(tmp_path, caminho)


@pytest.mark.parametrize("comando", [
    "sudo ls",
    "pip install requests",
    "python -m pip install requests",
    "shutdown now",
    "reboot",
    "rm -rf /",
    "rm -rf ~",
    "rm -fr *",
    "ls && sudo rm a",
])
def test_comandos_perigosos_sao_recusados(comando):
    permitido, motivo = validar_comando(comando)
    assert permitido is False
    assert motivo != ""


@pytest.mark.parametrize("comando", [
    "pytest -q",
    "ls -la",
    "rm arquivo.txt",
    "python -m pytest tests",
])
def test_comandos_normais_sao_permitidos(comando):
    permitido, motivo = validar_comando(comando)
    assert permitido is True


def test_comando_vazio_e_recusado():
    assert validar_comando("")[0] is False

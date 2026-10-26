import pytest

from minicode.cli import main as cli


def sem_dotenv(monkeypatch):
    # os testes não leem o .env de verdade: só o que o próprio teste define
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)


def test_variaveis_vazias_dao_uma_mensagem_clara_e_nao_um_traceback(monkeypatch, capsys):
    sem_dotenv(monkeypatch)
    for nome in cli.VARIAVEIS_DE_AMBIENTE:
        monkeypatch.setenv(nome, "")   # o .env.example copiado e não preenchido

    with pytest.raises(SystemExit) as saida:
        cli.conferir_ambiente()

    texto = capsys.readouterr().out
    assert saida.value.code == 2
    assert "MINICODE_API_BASE" in texto and "MINICODE_API_KEY" in texto and "MINICODE_MODEL" in texto
    assert ".env" in texto


def test_so_aponta_as_variaveis_que_faltam(monkeypatch, capsys):
    sem_dotenv(monkeypatch)
    monkeypatch.setenv("MINICODE_API_BASE", "http://localhost/v1")
    monkeypatch.setenv("MINICODE_API_KEY", "chave")
    monkeypatch.delenv("MINICODE_MODEL", raising=False)

    with pytest.raises(SystemExit):
        cli.conferir_ambiente()

    texto = capsys.readouterr().out
    assert "MINICODE_MODEL" in texto and "MINICODE_API_BASE" not in texto


def test_com_tudo_preenchido_segue_em_frente(monkeypatch):
    sem_dotenv(monkeypatch)
    for nome in cli.VARIAVEIS_DE_AMBIENTE:
        monkeypatch.setenv(nome, "valor")

    assert cli.conferir_ambiente() is None

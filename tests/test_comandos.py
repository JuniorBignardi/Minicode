import json
import sys

import pytest

from minicode.agent.conversas.fases import executar_acao
from minicode.agent.gates.comandos import desfazer_alteracoes, executar_comando, fotografar
from minicode.agent.maquina.estados import Execucao, FERRAMENTAS_POR_ESTADO, IMPLEMENTING, RECEIVED
from minicode.safety.comandos import validar_comando
from minicode.tools.comandos import run_command
from minicode.tracing.registro import iniciar_registro


# --- o validador conhece a raiz do projeto ---

@pytest.mark.parametrize("comando", [
    "cat /etc/passwd",
    "cat ../fora.txt",
    "ls ~/",
    r"type C:\Windows\system.ini",
    "python ../../script.py",
])
def test_argumento_que_aponta_para_fora_do_projeto_e_recusado(tmp_path, comando):
    permitido, motivo = validar_comando(comando, tmp_path)
    assert permitido is False and "fora do projeto" in motivo


def test_caminho_dentro_do_projeto_e_comando_normal_sao_permitidos(tmp_path):
    assert validar_comando("python src/app.py --opcao 1/2", tmp_path) == (True, "")


def test_sem_a_raiz_o_validador_continua_igual():
    assert validar_comando("cat /etc/passwd") == (True, "")


# --- a ferramenta ---

def test_run_command_executa_e_devolve_a_saida(tmp_path):
    ok, texto = run_command(tmp_path, 'python -c "print(2 + 3)"')
    assert ok is True and "5" in texto and "código de saída 0" in texto


def test_run_command_com_erro_devolve_false_e_o_traceback(tmp_path):
    ok, texto = run_command(tmp_path, 'python -c "import modulo_que_nao_existe"')
    assert ok is False and "ModuleNotFoundError" in texto


@pytest.mark.parametrize("comando", ["sudo ls", "rm -rf /", "shutdown now", "reboot"])
def test_run_command_recusa_comando_perigoso_sem_executar(tmp_path, comando):
    ok, texto = run_command(tmp_path, comando)
    assert ok is False and "recusado" in texto


def test_run_command_recusa_caminho_fora_do_projeto(tmp_path):
    ok, texto = run_command(tmp_path, "python ../fora.py")
    assert ok is False and "fora do projeto" in texto


def test_run_command_comando_inexistente_e_comando_vazio(tmp_path):
    assert run_command(tmp_path, "programa_que_nao_existe_xyz")[0] is False
    assert run_command(tmp_path, "   ")[0] is False
    assert run_command(tmp_path, 123)[0] is False


def test_run_command_roda_dentro_do_projeto(tmp_path):
    (tmp_path / "dados.txt").write_text("conteudo", encoding="utf-8")
    ok, texto = run_command(tmp_path, 'python -c "print(open(\'dados.txt\').read())"')
    assert ok is True and "conteudo" in texto


def test_run_command_nao_passa_a_chave_de_api(tmp_path, monkeypatch):
    monkeypatch.setenv("MINICODE_API_KEY", "segredo-123")
    ok, texto = run_command(tmp_path, 'python -c "import os; print(os.environ.get(\'MINICODE_API_KEY\'))"')
    assert "segredo-123" not in texto and "None" in texto


def test_run_command_tem_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr("minicode.tools.comandos.TIMEOUT_COMANDO", 1)
    ok, texto = run_command(tmp_path, 'python -c "import time; time.sleep(5)"')
    assert ok is False and "passou de 1s" in texto


# --- o gate: o comando não grava arquivos ---

def test_fotografia_ignora_as_pastas_internas(tmp_path):
    (tmp_path / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / ".minicode").mkdir()
    (tmp_path / ".minicode" / "state.json").write_text("{}", encoding="utf-8")
    assert list(fotografar(tmp_path)) == ["a.py"]


def test_arquivo_criado_alterado_e_apagado_pelo_comando_volta_ao_que_era(tmp_path):
    (tmp_path / "a.py").write_text("original", encoding="utf-8")
    (tmp_path / "b.py").write_text("vai sumir", encoding="utf-8")
    antes = fotografar(tmp_path)

    (tmp_path / "a.py").write_text("alterado", encoding="utf-8")
    (tmp_path / "b.py").unlink()
    (tmp_path / "novo.py").write_text("criado", encoding="utf-8")

    assert desfazer_alteracoes(tmp_path, antes) == ["a.py", "b.py", "novo.py"]
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "original"
    assert (tmp_path / "b.py").read_text(encoding="utf-8") == "vai sumir"
    assert not (tmp_path / "novo.py").exists()


def test_comando_que_grava_arquivo_tem_a_gravacao_desfeita_e_avisa(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    (tmp_path / "test_a.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")

    ok, texto = executar_comando(tmp_path, {"comando": 'python -c "open(\'test_a.py\', \'w\').write(\'lixo\')"'})

    assert (tmp_path / "test_a.py").read_text(encoding="utf-8") == "def test_a():\n    assert True\n"
    assert "desfez" in texto and "test_a.py" in texto
    eventos = (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8")
    assert "comando_desfeito" in eventos


def test_comando_que_nao_grava_nada_nao_gera_aviso(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    ok, texto = executar_comando(tmp_path, {"comando": 'python -c "print(1)"'})
    assert ok is True and "desfez" not in texto


def test_argumentos_errados_viram_erro_para_a_llm(tmp_path):
    ok, texto = executar_comando(tmp_path, {"cmd": "ls"})
    assert ok is False and "argumentos inválidos" in texto


# --- integração com o agente ---

def test_run_command_so_existe_na_implementacao():
    assert "run_command" in FERRAMENTAS_POR_ESTADO[IMPLEMENTING]
    assert "run_command" not in FERRAMENTAS_POR_ESTADO[RECEIVED]


def test_o_agente_executa_run_command_e_registra_a_chamada(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    execucao = Execucao("tarefa")
    execucao.estado = IMPLEMENTING

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "run_command", "args": {"comando": 'python -c "print(7)"'}})

    assert ok is True and "7" in texto
    eventos = [json.loads(l) for l in (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(e.get("tool") == "run_command" for e in eventos)


def test_run_command_e_negado_fora_da_implementacao(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    execucao = Execucao("tarefa")
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "run_command", "args": {"comando": "python -V"}})
    assert ok is False and "não é permitida" in texto

import json

from minicode.agent.estados import Execucao
from minicode.tracing.registro import (
    iniciar_registro, registrar_evento, salvar_documento, salvar_estado,
)


def ler_eventos(raiz):
    linhas = (raiz / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


def test_iniciar_cria_a_pasta(tmp_path):
    iniciar_registro(tmp_path, "criar fatorial")
    assert (tmp_path / ".minicode").is_dir()


def test_iniciar_apaga_eventos_da_execucao_anterior(tmp_path):
    iniciar_registro(tmp_path, "tarefa 1")
    registrar_evento(tmp_path, {"tipo": "velho"})

    iniciar_registro(tmp_path, "tarefa 2")
    registrar_evento(tmp_path, {"tipo": "novo"})

    eventos = ler_eventos(tmp_path)
    assert [e["tipo"] for e in eventos] == ["novo"]


def test_registrar_evento_escreve_uma_linha_json_por_evento(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    registrar_evento(tmp_path, {"tipo": "ferramenta", "tool": "read_file", "ok": True})
    registrar_evento(tmp_path, {"tipo": "chamada_llm", "fase": "spec"})

    eventos = ler_eventos(tmp_path)
    assert len(eventos) == 2
    assert eventos[0]["tool"] == "read_file"
    assert eventos[0]["ok"] is True
    assert eventos[1]["fase"] == "spec"


def test_cada_evento_tem_a_hora(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    registrar_evento(tmp_path, {"tipo": "teste"})
    assert "hora" in ler_eventos(tmp_path)[0]


def test_acentos_ficam_legiveis_no_arquivo(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    registrar_evento(tmp_path, {"mensagem": "ação inválida"})
    texto = (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8")
    assert "ação inválida" in texto


def test_salvar_documento(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    salvar_documento(tmp_path, "specification.md", "# Specification\n")
    texto = (tmp_path / ".minicode" / "specification.md").read_text(encoding="utf-8")
    assert texto == "# Specification\n"


def test_salvar_estado(tmp_path):
    iniciar_registro(tmp_path, "criar fatorial")
    execucao = Execucao("criar fatorial")
    execucao.tentativas = 2
    execucao.registrar_escrita("fat.py")

    salvar_estado(tmp_path, execucao)

    estado = json.loads((tmp_path / ".minicode" / "state.json").read_text(encoding="utf-8"))
    assert estado["tarefa"] == "criar fatorial"
    assert estado["estado"] == "RECEIVED"
    assert estado["tentativas"] == 2
    assert estado["arquivos_alterados"] == ["fat.py"]
    assert estado["testes_passaram"] is False


def test_salvar_estado_sobrescreve_o_anterior(tmp_path):
    iniciar_registro(tmp_path, "tarefa")
    execucao = Execucao("tarefa")
    salvar_estado(tmp_path, execucao)
    execucao.tentativas = 3
    salvar_estado(tmp_path, execucao)

    estado = json.loads((tmp_path / ".minicode" / "state.json").read_text(encoding="utf-8"))
    assert estado["tentativas"] == 3

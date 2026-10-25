import json

from minicode.agent.orquestrador import rodar_agente

SPEC = """<spec>
# Specification

## Objective
Criar a função dobro.

## Acceptance Criteria
- dobro(2) == 4
- dobro(0) == 0
</spec>"""

PLANO = "<plan>\n1. criar dobro.py\n2. criar testes\n</plan>"

APROVADA = json.dumps({"criterios": [{"criterio": "x", "atendido": True, "motivo": "ok"}]})
SPEC_COBERTA = json.dumps({"requisitos": [{"requisito": "x", "coberto": True, "motivo": "ok"}]})
DIAGNOSTICO = json.dumps({"classificacao": "UNKNOWN", "evidencias": "e", "proxima_acao": "p"})


def acao(tool, **args):
    return json.dumps({"tool": tool, "args": args})


def chat_falso(respostas):
    fila = list(respostas)

    def chat(mensagens, temperature=0, **kw):
        nome = kw.get("response_format", {}).get("json_schema", {}).get("name")
        if nome == "revisao":
            return APROVADA
        if nome == "revisao_spec":
            return SPEC_COBERTA
        if nome == "diagnostico":
            return DIAGNOSTICO
        return fila.pop(0)

    return chat


def rodar(tmp_path, **kw):
    chat = chat_falso([
        SPEC, PLANO,
        acao("write_file", path="dobro.py", content="def dobro(n):\n    return n * 2\n"),
        acao("write_file", path="tests/test_dobro.py", content="from dobro import dobro\n\ndef test_a():\n    assert dobro(2) == 4\n"),
        acao("finish"),
    ])
    return rodar_agente("crie dobro", tmp_path, chat, **kw, planejar_testes=False)


def ler_debug(tmp_path):
    linhas = (tmp_path / ".minicode" / "debug.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


def test_depuracao_desligada_nao_cria_o_arquivo(tmp_path, monkeypatch):
    monkeypatch.delenv("MINICODE_DEBUG", raising=False)
    rodar(tmp_path)
    assert not (tmp_path / ".minicode" / "debug.jsonl").exists()


def test_depuracao_pode_ser_ligada_pela_variavel_de_ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("MINICODE_DEBUG", "1")
    rodar(tmp_path)
    assert (tmp_path / ".minicode" / "debug.jsonl").exists()


def test_depuracao_grava_o_fluxo_completo(tmp_path):
    rodar(tmp_path, modo_debug=True)
    eventos = ler_debug(tmp_path)
    tipos = {e["tipo"] for e in eventos}

    assert {"inicio", "llm_pedido", "llm_resposta", "ferramenta", "mudanca_estado",
            "arquivos_para_verificacao", "saida_testes", "fim"} <= tipos

    # a ordem (seq) é crescente e sem buracos
    assert [e["seq"] for e in eventos] == list(range(1, len(eventos) + 1))


def test_cada_chamada_a_llm_guarda_as_mensagens_completas_e_a_resposta(tmp_path):
    rodar(tmp_path, modo_debug=True)
    eventos = ler_debug(tmp_path)

    pedidos = [e for e in eventos if e["tipo"] == "llm_pedido"]
    respostas = [e for e in eventos if e["tipo"] == "llm_resposta"]
    assert len(pedidos) == len(respostas)

    # o pedido da implementação leva a spec e o plano inteiros, e o schema de ação
    implementacao = [p for p in pedidos if p["fase"] == "implementacao"][0]
    usuario = implementacao["mensagens"][1]["content"]
    assert "dobro(2) == 4" in usuario and "criar dobro.py" in usuario
    assert implementacao["schema"] == "acao"
    assert implementacao["caracteres"] == sum(len(m["content"]) for m in implementacao["mensagens"])


def test_saida_dos_testes_e_resultado_das_ferramentas_ficam_completos(tmp_path):
    rodar(tmp_path, modo_debug=True)
    eventos = ler_debug(tmp_path)

    escrita = [e for e in eventos if e["tipo"] == "ferramenta" and e["ferramenta"] == "write_file"][0]
    assert escrita["args"]["content"] == "def dobro(n):\n    return n * 2\n"

    testes = [e for e in eventos if e["tipo"] == "saida_testes"][0]
    assert testes["passou"] is True and testes["cortado"] is False

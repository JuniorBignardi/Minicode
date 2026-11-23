import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "experiments" / "diagnostico_parte1"))

import atribuir_falhas  # noqa: E402
import oraculo  # noqa: E402
import rodar_instrumentado  # noqa: E402

TESTE_ERRADO = "from fatorial import fatorial\n\ndef test_cinco():\n    assert fatorial(5) == 100\n"


def linhas_do_registro(raiz):
    arquivo = raiz / ".minicode" / "chamadas_llm.jsonl"
    return [json.loads(linha) for linha in arquivo.read_text(encoding="utf-8").splitlines()]


def test_a_fase_vem_do_schema_ou_da_temperatura():
    formato = {"type": "json_schema", "json_schema": {"name": "plano_de_testes", "schema": {}}}
    assert rodar_instrumentado.fase_da_chamada(0.3, {"response_format": formato}) == "plano_de_testes"
    assert rodar_instrumentado.fase_da_chamada(0.6, {}) == "spec"
    assert rodar_instrumentado.fase_da_chamada(0.5, {}) == "plano"


def test_cada_chamada_e_registrada_com_as_mensagens_de_antes_da_resposta(tmp_path):
    def chat_real(mensagens, temperature=0, **kw):
        return "resposta"

    chat = rodar_instrumentado.criar_chat(chat_real, tmp_path)
    mensagens = [{"role": "user", "content": "oi"}]
    assert chat(mensagens, temperature=0.6) == "resposta"
    mensagens.append({"role": "assistant", "content": "resposta"})   # o agente faz isso depois da chamada

    registro = linhas_do_registro(tmp_path)
    assert len(registro) == 1 and registro[0]["fase"] == "spec" and registro[0]["resposta"] == "resposta"
    assert len(registro[0]["mensagens"]) == 1


def test_o_diagnostico_guarda_uma_copia_do_projeto_sem_o_rastro(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / ".minicode").mkdir()
    formato = {"type": "json_schema", "json_schema": {"name": "diagnostico", "schema": {}}}

    chat = rodar_instrumentado.criar_chat(lambda m, temperature=0, **kw: "{}", tmp_path)
    chat([{"role": "user", "content": "x"}], temperature=0.2, response_format=formato)

    copia = tmp_path / ".minicode" / "snapshots" / "diag_01"
    assert (copia / "a.py").is_file() and not (copia / ".minicode").exists()


def test_chamada_que_falha_e_registrada_e_o_erro_continua_subindo(tmp_path):
    def chat_real(mensagens, temperature=0, **kw):
        raise RuntimeError("rede fora do ar")

    chat = rodar_instrumentado.criar_chat(chat_real, tmp_path)
    try:
        chat([{"role": "user", "content": "x"}])
        assert False, "deveria ter levantado"
    except RuntimeError:
        pass
    assert "rede fora do ar" in linhas_do_registro(tmp_path)[0]["erro"]


def montar_execucao(tmp_path):
    # FAILED com o código certo, mas com um teste errado e um diagnóstico que acusou o código
    pasta = tmp_path / "facil_r1" / "tarefa_01"
    (pasta / "tests").mkdir(parents=True)
    (pasta / "fatorial.py").write_text(oraculo.REFERENCIAS_FACEIS[1]["fatorial.py"], encoding="utf-8")
    (pasta / "tests" / "test_f.py").write_text(TESTE_ERRADO, encoding="utf-8")

    snapshot = pasta / ".minicode" / "snapshots" / "diag_01"
    (snapshot / "tests").mkdir(parents=True)
    (snapshot / "fatorial.py").write_text(oraculo.REFERENCIAS_FACEIS[1]["fatorial.py"], encoding="utf-8")
    (snapshot / "tests" / "test_f.py").write_text(TESTE_ERRADO, encoding="utf-8")
    (pasta / ".minicode" / "actions.jsonl").write_text(json.dumps({"tipo": "diagnostico", "classificacao": "CODE_BUG"}) + "\n", encoding="utf-8")

    resultado = {"id": 1, "nome": "fatorial", "tipo": "implementar", "estado": "FAILED", "codigo_correto": True, "reparos": 3,
                 "chamadas": 30, "segundos": 60, "arquivos_alterados": ["fatorial.py", "tests/test_f.py"],
                 "plano_de_testes": [{"criterio": "c", "entrada": "fatorial(5)", "esperado": "120"},
                                     {"criterio": "c", "entrada": "fatorial(3)", "esperado": "7"}]}
    (pasta / "resultado.json").write_text(json.dumps(resultado), encoding="utf-8")
    return pasta


def test_a_analise_acha_o_plano_o_teste_e_o_diagnostico_errados(tmp_path):
    analise = atribuir_falhas.analisar_execucao(montar_execucao(tmp_path), "facil")

    assert analise["categoria"] == "FAILED com código certo"
    assert analise["casos"] == {"correto": 1, "errado": 1}
    assert analise["plano_errado"] is True
    assert analise["testes_do_agente_errados"] is True
    assert analise["diagnosticos"][0]["oraculo"] == "TEST_BUG" and analise["diagnosticos"][0]["modelo"] == "CODE_BUG"
    assert analise["diagnostico_errado"] is True


def test_o_relatorio_aponta_a_etapa_lider(tmp_path):
    analise = atribuir_falhas.analisar_execucao(montar_execucao(tmp_path), "facil")
    texto = atribuir_falhas.relatorio([analise])

    assert "FAILED com código certo" in texto
    assert "Etapa líder" in texto and "plano de testes com valor esperado errado" in texto

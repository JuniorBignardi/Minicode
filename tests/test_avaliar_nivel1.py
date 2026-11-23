import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments" / "nivel1"))
sys.path.insert(0, str(RAIZ / "experiments" / "gabarito"))
sys.path.insert(0, str(RAIZ / "src"))

import avaliar_nivel1  # noqa: E402

SPEC = "# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- soma dois números\n- levanta ValueError para texto"
USUARIO = f"Pedido do usuário:\nfaça soma\n\nEspecificação:\n{SPEC}\n\nPlano:\n1. a\n2. b\n\nDefina os casos de teste."


def plano(*casos):
    return json.dumps({"casos": [{"criterio": c, "entrada": "soma(1, 2)", "esperado": "3"} for c in casos]})


def montar_logs(tmp_path):
    # uma execução com duas chamadas do plano de testes: a mesma entrada repetida e uma outra
    pasta = tmp_path / "r1" / "tarefa_01" / ".minicode"
    pasta.mkdir(parents=True)
    chamadas = [
        {"fase": "plano_de_testes", "mensagens": [{"role": "system", "content": "s"}, {"role": "user", "content": USUARIO}], "resposta": plano("soma dois números", "levanta ValueError para texto")},
        {"fase": "plano_de_testes", "mensagens": [{"role": "system", "content": "s"}, {"role": "user", "content": USUARIO}], "resposta": "repetida"},
        {"fase": "revisao_plano_de_testes", "mensagens": [{"role": "system", "content": "s"}, {"role": "user", "content": "outra"}], "resposta": "{}"},
    ]
    (pasta / "chamadas_llm.jsonl").write_text("".join(json.dumps(c) + "\n" for c in chamadas), encoding="utf-8")
    (tmp_path / "diagnostico_falhas.json").write_text(json.dumps([{"id": 1, "conjunto": "facil", "rodada": "r1"}]), encoding="utf-8")
    return tmp_path


def test_entradas_reais_usam_so_o_plano_de_testes_e_nao_repetem(tmp_path):
    entradas = avaliar_nivel1.entradas_reais(montar_logs(tmp_path))
    assert len(entradas) == 1 and entradas[0]["conjunto"] == "facil" and entradas[0]["id"] == 1
    assert entradas[0]["resposta_14b"].startswith('{"casos"')


def test_spec_e_json_com_texto_em_volta():
    assert "soma dois números" in avaliar_nivel1.spec_da_mensagem(USUARIO)
    assert len(avaliar_nivel1.interpretar("Aqui está:\n```json\n" + plano("a") + "\n```")) == 1
    assert avaliar_nivel1.interpretar("sem json") is None


def test_pontuar_conta_formato_plano_valido_e_notas_do_oraculo(tmp_path, monkeypatch):
    entradas = avaliar_nivel1.entradas_reais(montar_logs(tmp_path))
    monkeypatch.setattr(avaliar_nivel1.oraculo, "avaliar_casos", lambda conjunto, id, casos: ["correto", "errado"][:len(casos)])

    completo = avaliar_nivel1.pontuar(entradas)[0]
    assert completo["formato_ok"] and completo["plano_valido"] and completo["notas"] == ["correto", "errado"]

    incompleto = avaliar_nivel1.pontuar(entradas, gerar=lambda m: plano("soma dois números"))[0]
    assert incompleto["formato_ok"] and not incompleto["plano_valido"]

    quebrado = avaliar_nivel1.pontuar(entradas, gerar=lambda m: "nada")[0]
    assert not quebrado["formato_ok"] and quebrado["notas"] == []


def test_resumo_calcula_a_fracao_correta_e_o_intervalo():
    resultados = [{"tarefa": f"t{i}", "formato_ok": True, "plano_valido": True, "notas": ["correto"] * 3 + ["errado"] + ["inavaliavel"]} for i in range(5)]
    r = avaliar_nivel1.resumo(resultados, repeticoes=200)
    assert r["casos_corretos"] == 15 and r["casos_errados"] == 5 and r["casos_inavaliaveis"] == 5
    assert r["fracao_correta"] == 0.75 and r["ic95"][0] == r["ic95"][1] == 0.75


def test_fracao_sem_casos_avaliaveis_e_none():
    assert avaliar_nivel1.fracao_correta(["inavaliavel"]) is None


def test_sem_os_logs_da_parte_1_usa_os_prompts_versionados(tmp_path):
    entradas = avaliar_nivel1.entradas_reais(tmp_path)   # pasta sem diagnostico_falhas.json
    assert len(entradas) == 60
    assert all({"conjunto", "id", "mensagens"} <= set(e) for e in entradas)
    assert all("resposta_14b" not in e for e in entradas)

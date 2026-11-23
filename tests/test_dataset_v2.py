import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments" / "dataset"))
sys.path.insert(0, str(RAIZ / "experiments" / "gabarito"))

import gerar_v2  # noqa: E402
import professor  # noqa: E402

CRITERIOS_JOGO = [
    "Cada acerto vale 10 pontos e cada erro desconta 3 pontos.",
    "A pontuação nunca fica abaixo de zero.",
    "Levanta ValueError se acertos ou erros forem negativos.",
]
SPEC_JOGO = "# Specification\n\n## Objective\nCalcular a pontuação de um jogo.\n\n## Acceptance Criteria\n" + "\n".join(f"- {c}" for c in CRITERIOS_JOGO)


def caso(criterio, entrada):
    return {"criterio": criterio, "entrada": entrada}


JOGO = {
    "arquivo": "jogo.py",
    "pedido": "Crie em jogo.py a função pontos_do_jogo(acertos, erros) que dá 10 pontos por acerto menos 3 por erro, nunca abaixo de zero, e levanta ValueError se algum valor for negativo.",
    "referencia": "def pontos_do_jogo(acertos, erros):\n    if acertos < 0 or erros < 0:\n        raise ValueError('negativo')\n    return max(0, acertos * 10 - erros * 3)\n",
    "especificacao": SPEC_JOGO,
    "plano": "1. Criar o arquivo jogo.py.\n2. Implementar a função.\n3. Escrever os testes.",
    "casos": [caso(CRITERIOS_JOGO[0], "pontos_do_jogo(1, 0)"), caso(CRITERIOS_JOGO[0], "pontos_do_jogo(2, 3)"),
              caso(CRITERIOS_JOGO[0], "pontos_do_jogo(5, 1)"), caso(CRITERIOS_JOGO[0], "pontos_do_jogo(10, 10)"),
              caso(CRITERIOS_JOGO[1], "pontos_do_jogo(0, 5)"), caso(CRITERIOS_JOGO[1], "pontos_do_jogo(0, 0)"),
              caso(CRITERIOS_JOGO[2], "pontos_do_jogo(-1, 0)"), caso(CRITERIOS_JOGO[2], "pontos_do_jogo(3, -2)")],
}

CRITERIOS_FRETE = ["Pesos de até 2 kg custam 8 reais.", "Cada quilo inteiro acima de 2 kg soma 3 reais.", "Peso zero ou negativo levanta ValueError."]
FRETE = {
    "arquivo": "loja.py",
    "pedido": "Faça em loja.py a função frete_da_encomenda(peso) que cobra 8 reais até 2 kg e mais 3 reais por kg extra inteiro, e levanta ValueError para peso zero ou negativo.",
    "referencia": "def frete_da_encomenda(peso):\n    if peso <= 0:\n        raise ValueError('peso')\n    return 8 + max(0, int(peso) - 2) * 3\n",
    "especificacao": "# Specification\n\n## Objective\nCalcular o frete.\n\n## Acceptance Criteria\n" + "\n".join(f"- {c}" for c in CRITERIOS_FRETE),
    "plano": "1. Criar loja.py.\n2. Implementar o frete.\n3. Testar.",
    "casos": [caso(CRITERIOS_FRETE[0], "frete_da_encomenda(1)"), caso(CRITERIOS_FRETE[0], "frete_da_encomenda(2)"),
              caso(CRITERIOS_FRETE[1], "frete_da_encomenda(3)"), caso(CRITERIOS_FRETE[1], "frete_da_encomenda(5)"),
              caso(CRITERIOS_FRETE[1], "frete_da_encomenda(10)"), caso(CRITERIOS_FRETE[1], "frete_da_encomenda(2.5)"),
              caso(CRITERIOS_FRETE[2], "frete_da_encomenda(0)"), caso(CRITERIOS_FRETE[1], "frete_da_encomenda(4)")],
}


def com(base, **mudancas):
    return {**base, **mudancas}


def em_blocos(exercicio, cerca=False):
    # a resposta do professor no formato pedido: seis blocos entre tags
    partes = []
    for tag in ("arquivo", "pedido", "referencia", "especificacao", "plano", "casos"):
        valor = exercicio[tag]
        if tag == "casos":
            valor = json.dumps(valor, ensure_ascii=False)
        elif tag == "referencia" and cerca:
            valor = "```python\n" + valor + "```"
        partes.append(f"<{tag}>\n{valor}\n</{tag}>")
    return "\n".join(partes)


def test_exercicio_bom_ganha_os_valores_esperados_da_execucao():
    registro, motivo = gerar_v2.validar_exercicio(JOGO)
    assert motivo == ""
    esperados = {c["entrada"]: c["esperado"] for c in registro["casos"]}
    assert esperados["pontos_do_jogo(2, 3)"] == "11" and esperados["pontos_do_jogo(-1, 0)"] == "ValueError"
    assert registro["nome"] == "pontos_do_jogo" and len(registro["casos"]) == 8


def test_criterio_que_o_modelo_escreveu_com_pequena_diferenca_ainda_e_associado():
    casos = [dict(c) for c in JOGO["casos"]]
    casos[0]["criterio"] = "- " + CRITERIOS_JOGO[0].rstrip(".")
    registro, motivo = gerar_v2.validar_exercicio(com(JOGO, casos=casos))
    assert motivo == "" and registro["casos"][0]["criterio"] == CRITERIOS_JOGO[0]


def test_criterio_sem_nenhum_caso_e_recusado():
    casos = [c for c in JOGO["casos"] if c["criterio"] != CRITERIOS_JOGO[2]]
    assert gerar_v2.validar_exercicio(com(JOGO, casos=casos))[1] == "algum critério ficou sem caso"


def test_spec_sem_a_secao_de_objetivo_e_recusada():
    assert gerar_v2.validar_exercicio(com(JOGO, especificacao="## Acceptance Criteria\n- a\n- b\n- c"))[1] == "spec inválida"


def test_poucos_criterios_e_plano_invalido_sao_recusados():
    spec = "# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- um\n- dois\n"
    assert gerar_v2.validar_exercicio(com(JOGO, especificacao=spec))[1] == "poucos critérios"
    assert gerar_v2.validar_exercicio(com(JOGO, plano="faça tudo de uma vez"))[1] == "plano inválido"


def test_resposta_sem_json_ou_com_campos_faltando():
    assert gerar_v2.validar_exercicio(None)[1] == "resposta sem os blocos"
    assert gerar_v2.validar_exercicio({"arquivo": "a.py"})[1] == "campos faltando ou com tipo errado"


def test_spec_que_entrega_os_resultados_e_recusada():
    referencia = "def rotular(n):\n    if n < 0:\n        raise ValueError('negativo')\n    return 'item_' + str(n)\n"
    criterios = ["rotular(1) devolve 'item_1'", "rotular(2) devolve 'item_2' e rotular(3) devolve 'item_3'", "rotular(4) devolve 'item_4' e rotular(-1) levanta ValueError"]
    spec = "# Specification\n\n## Objective\nRotular.\n\n## Acceptance Criteria\n" + "\n".join(f"- {c}" for c in criterios)
    casos = [caso(criterios[0], "rotular(1)"), caso(criterios[0], "rotular(5)"), caso(criterios[1], "rotular(2)"), caso(criterios[1], "rotular(3)"),
             caso(criterios[1], "rotular(6)"), caso(criterios[2], "rotular(4)"), caso(criterios[2], "rotular(-1)"), caso(criterios[2], "rotular(0)")]
    exercicio = {"arquivo": "rotulos.py", "pedido": "Crie em rotulos.py a função rotular(n) que devolve 'item_' e o número, e levanta ValueError para negativos.",
                 "referencia": referencia, "especificacao": spec.replace("rotular(5)", "x"), "plano": "1. Criar.\n2. Implementar.", "casos": casos}
    spec_que_entrega = spec + "\n- rotular(5) devolve 'item_5' e rotular(6) devolve 'item_6' e rotular(0) devolve 'item_0'"
    resultado = gerar_v2.validar_exercicio(com(exercicio, especificacao=spec_que_entrega, casos=casos))
    assert resultado[1] == "algum critério ficou sem caso" or resultado[1] == "a spec entrega os resultados"


def test_exemplo_de_treino_usa_o_prompt_do_agente_e_o_plano_de_testes_certo():
    registro, _ = gerar_v2.validar_exercicio(JOGO)
    exemplo = gerar_v2.exemplo_de_treino({"id": "v0001", "modelo": "m", **registro})

    sistema, usuario = (m["content"] for m in exemplo["mensagens"])
    assert "engenheiro de testes" in sistema
    assert "Pedido do usuário:" in usuario and "Especificação:" in usuario and "Plano:" in usuario
    casos = json.loads(exemplo["resposta"])["casos"]
    assert len(casos) == 8 and set(casos[0]) == {"criterio", "entrada", "esperado"}
    assert {c["criterio"] for c in casos} == set(CRITERIOS_JOGO)


class ProfessorDeMentira:
    modelo = "modelo-de-mentira"

    def __init__(self, respostas):
        self.respostas = list(respostas)

    def __call__(self, mensagens, temperature=0.7, max_tokens=3000):
        return self.respostas.pop(0)


def test_gerar_grava_so_os_validos_e_nao_repete(tmp_path):
    prof = ProfessorDeMentira(["Aqui está:\n" + em_blocos(JOGO, cerca=True), em_blocos(JOGO), "isto não tem blocos", em_blocos(FRETE)])
    registros = gerar_v2.gerar(prof, tmp_path / "v2.jsonl", 2, threads=1, log=lambda m: None)

    assert [r["nome"] for r in registros] == ["pontos_do_jogo", "frete_da_encomenda"]
    linhas = [json.loads(l) for l in (tmp_path / "v2.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [l["id"] for l in linhas] == ["v0001", "v0002"] and linhas[0]["modelo"] == "modelo-de-mentira"


def test_gerar_para_quando_o_professor_so_devolve_lixo(tmp_path):
    prof = ProfessorDeMentira(["lixo"] * 60)
    assert gerar_v2.gerar(prof, tmp_path / "v2.jsonl", 1, threads=1, log=lambda m: None) == []


def test_limite_de_taxa_espera_quando_ja_usou_todas_as_chamadas_do_minuto(monkeypatch):
    limite = professor.LimiteDeTaxa(2)
    esperas = []
    monkeypatch.setattr(professor.time, "sleep", lambda s: (esperas.append(s), limite.instantes.clear()))
    for _ in range(3):
        limite.esperar()
    assert len(esperas) == 1 and esperas[0] > 0


def test_a_leitura_dos_blocos_tira_a_cerca_de_codigo_e_le_os_casos():
    exercicio = gerar_v2.extrair_exercicio("texto solto\n" + em_blocos(JOGO, cerca=True) + "\nmais texto")
    assert exercicio["referencia"].startswith("def pontos_do_jogo") and "```" not in exercicio["referencia"]
    assert len(exercicio["casos"]) == 8 and exercicio["plano"].startswith("1.")


def test_resposta_sem_algum_bloco_ou_com_casos_que_nao_sao_json_nao_serve():
    assert gerar_v2.extrair_exercicio(em_blocos(JOGO).replace("<plano>", "<outro>").replace("</plano>", "</outro>")) is None
    sem_json = em_blocos(JOGO).replace("[{", "{{").replace("}]", "}}")
    assert gerar_v2.extrair_exercicio(sem_json) is None

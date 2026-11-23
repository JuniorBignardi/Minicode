import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments" / "dataset"))
sys.path.insert(0, str(RAIZ / "experiments" / "gabarito"))

import montar_dataset  # noqa: E402


def registro(nome, modelo, pedido=None):
    criterio = f"{nome} devolve o dobro"
    return {"id": "v0001", "modelo": modelo, "tema": "t", "estilo": "uma função", "regras": 1, "nome": nome, "arquivo": f"{nome}.py",
            "pedido": pedido or f"Crie em {nome}.py a função {nome} que calcula algo único de {nome}.",
            "referencia": f"def {nome}(x):\n    return 2 * x\n", "especificacao": f"# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- {criterio}",
            "plano": "1. Criar.\n2. Testar.", "casos": [{"criterio": criterio, "entrada": f"{nome}(2)", "esperado": "4"}]}


def gravar(caminho, registros):
    caminho.write_text("".join(json.dumps(r) + "\n" for r in registros), encoding="utf-8")
    return caminho


def test_repetidos_por_nome_ou_pedido_parecido_sao_tirados():
    a, b = registro("soma", "m1"), registro("soma", "m2")
    c = registro("outra", "m2", pedido=a["pedido"])
    mantidos, tirados = montar_dataset.sem_repetidos([a, b, c, registro("diferente", "m1", pedido="Escreva em outro.py a classe Estoque que guarda produtos e quantidades e remove itens vendidos.")])
    assert [r["nome"] for r in mantidos] == ["soma", "diferente"] and tirados == 2


def test_divisao_separa_por_professor_e_nao_repete_exercicio():
    registros = [registro(f"f{i}", "m1") for i in range(20)] + [registro(f"g{i}", "m2") for i in range(10)]
    partes = montar_dataset.dividir(registros)
    assert {n: len(v) for n, v in partes.items()} == {"treino": 24, "validacao": 3, "teste": 3}
    nomes = [r["nome"] for v in partes.values() for r in v]
    assert len(nomes) == len(set(nomes)) == 30
    assert all({r["modelo"] for r in v} == {"m1", "m2"} for v in partes.values())


def test_montar_grava_arquivos_ids_novos_e_exemplo_com_o_prompt_do_agente(tmp_path):
    arquivo = gravar(tmp_path / "a.jsonl", [registro(f"f{i}", "m1") for i in range(10)])
    partes, _, _ = montar_dataset.montar([arquivo], tmp_path / "saida")
    for nome in ("treino", "validacao", "teste"):
        assert (tmp_path / "saida" / f"registros_{nome}.jsonl").is_file()
    exemplo = json.loads((tmp_path / "saida" / "exemplos_treino.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert exemplo["tarefa_id"].startswith("e") and "engenheiro de testes" in exemplo["mensagens"][0]["content"]
    assert json.loads(exemplo["resposta"])["casos"][0]["esperado"] == "4"
    assert "Casos por exercício" in (tmp_path / "saida" / "relatorio.md").read_text(encoding="utf-8")


def caso(criterio, entrada, esperado):
    return {"criterio": criterio, "entrada": entrada, "esperado": esperado}


def test_caso_suspeito_pega_atributo_privado_e_levanta_com_valor():
    assert montar_dataset.caso_suspeito(caso("inicia vazio", "r = R(); r._itens", "[]"))
    assert montar_dataset.caso_suspeito(caso("Levanta ValueError se faltar dependência", "f({'a': ['b']})", "['b', 'a']"))
    assert not montar_dataset.caso_suspeito(caso("Levanta ValueError se faltar dependência", "f({'a': ['z']})", "ValueError"))
    assert not montar_dataset.caso_suspeito(caso("Soma e levanta ValueError se negativo", "f(2, 3)", "5"))


def test_filtro_tira_o_caso_ruim_e_o_exercicio_que_ficou_com_critério_sem_caso():
    spec = "# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- dobra o valor\n- levanta ValueError se negativo\n- valor zero devolve zero"
    base = registro("dobro", "m1")
    ok = {**base, "especificacao": spec, "casos": [caso("dobra o valor", "dobro(2)", "4"), caso("dobra o valor", "dobro(3)._x", "6"),
                                                    caso("levanta ValueError se negativo", "dobro(-1)", "ValueError"), caso("valor zero devolve zero", "dobro(0)", "0")]}
    perde_criterio = {**ok, "nome": "outro", "casos": [caso("dobra o valor", "outro(2)", "4"), caso("levanta ValueError se negativo", "outro(-1)", "-2"),
                                                       caso("valor zero devolve zero", "outro(0)", "0")]}
    mantidos, casos_tirados, exercicios_tirados = montar_dataset.filtrar_casos([ok, perde_criterio])
    assert [r["nome"] for r in mantidos] == ["dobro"] and len(mantidos[0]["casos"]) == 3
    assert casos_tirados == 1 and exercicios_tirados == 1


def test_filtro_tira_exercicio_com_criterios_em_ingles_e_casos_repetidos():
    ingles = {**registro("raiz", "m1"), "especificacao": "# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- Raises ValueError if the list is empty\n- Returns the sum when the list is valid\n- Handles negative numbers"}
    assert montar_dataset.criterios_em_ingles(ingles) and not montar_dataset.criterios_em_ingles(registro("soma", "m1"))
    c = caso("soma dois", "f(1, 2)", "3")
    assert montar_dataset.sem_casos_repetidos([c, dict(c), caso("outro", "f(1, 2)", "3")]) == [c, caso("outro", "f(1, 2)", "3")]


def test_exercicio_de_teste_parecido_com_o_do_treino_vai_para_o_treino():
    treino = [registro("converter_base", "m1", pedido="Converta numeros entre bases numericas binaria octal hexadecimal")]
    parecido = registro("converter_base_num", "m1", pedido="Converta numeros entre bases numericas binaria octal decimal")
    diferente = registro("fila", "m1", pedido="Simule uma fila de atendimento com prioridade e senhas")
    partes, movidos = montar_dataset.afastar_parecidos({"treino": treino, "validacao": [], "teste": [parecido, diferente]})
    assert movidos == 1 and [r["nome"] for r in partes["teste"]] == ["fila"] and len(partes["treino"]) == 2


def test_criterio_que_so_levanta_erro_mas_nenhum_caso_espera_erro_derruba_o_exercicio():
    spec = "# Specification\n\n## Objective\nx\n\n## Acceptance Criteria\n- soma os valores\n- uma parte sem igual levanta ValueError\n- não levanta exceção para lista vazia"
    contradiz = {**registro("f", "m1"), "especificacao": spec, "casos": [caso("soma os valores", "f(1, 2)", "3"), caso("uma parte sem igual levanta ValueError", "f('a')", "{'': 'a'}"),
                                                                       caso("não levanta exceção para lista vazia", "f([])", "[]")]}
    assert montar_dataset.criterio_de_erro_sem_caso_de_erro(contradiz)
    certo = {**contradiz, "casos": [contradiz["casos"][0], caso("uma parte sem igual levanta ValueError", "f('a')", "ValueError"), contradiz["casos"][2]]}
    assert not montar_dataset.criterio_de_erro_sem_caso_de_erro(certo)


def test_exclusao_por_leitura_e_formato_monetario_quebrado():
    base = registro("moeda", "m1")
    assert montar_dataset.excluido_por_leitura({**base, "arquivo": "content_negotiation.py"})
    assert montar_dataset.excluido_por_leitura({**base, "casos": [caso("c", "f(0)", "'R$,0,00'")]})
    assert montar_dataset.excluido_por_leitura({**base, "casos": [caso("c", "f(1)", "'R$ 001.234.567,89'")]})
    assert not montar_dataset.excluido_por_leitura({**base, "casos": [caso("c", "f(1)", "'R$ 1.234.567,89'")]})


def test_traducao_troca_a_spec_e_os_criterios_dos_casos_sem_mexer_nos_valores(tmp_path, monkeypatch):
    spec = "# Specification\n\n## Objective\nParse a line.\n\n## Acceptance Criteria\n- Raises ValueError if the list is empty\n- Returns the sum when the list is valid\n- Handles negative numbers"
    r = {**registro("somar", "m1"), "especificacao": spec,
         "casos": [caso("Raises ValueError if the list is empty", "somar([])", "ValueError"), caso("Returns the sum when the list is valid", "somar([1, 2])", "3"),
                   caso("Handles negative numbers", "somar([-1])", "-1")]}
    arquivo = tmp_path / "traducoes.json"
    arquivo.write_text(json.dumps({"somar": {"objetivo": "Somar valores.", "criterios": ["Levanta ValueError se a lista estiver vazia", "Retorna a soma quando a lista é válida", "Trata números negativos"]}}), encoding="utf-8")
    monkeypatch.setattr(montar_dataset, "TRADUCOES", arquivo)
    resultado, feitos = montar_dataset.aplicar_traducoes([r])
    assert feitos == 1 and not montar_dataset.criterios_em_ingles(resultado[0])
    assert [c["criterio"] for c in resultado[0]["casos"]][0] == "Levanta ValueError se a lista estiver vazia" and resultado[0]["casos"][1]["esperado"] == "3"


def test_correcao_de_referencia_executa_as_entradas_de_novo(tmp_path, monkeypatch):
    errada = "def dobro(x):\n    return x * 3\n"
    r = {**registro("dobro", "m1"), "arquivo": "dobro.py", "referencia": errada, "casos": [caso("dobra", "dobro(2)", "6")]}
    arquivo = tmp_path / "correcoes.json"
    arquivo.write_text(json.dumps({"dobro.py": [["x * 3", "x * 2"]]}), encoding="utf-8")
    monkeypatch.setattr(montar_dataset, "CORRECOES_DE_REFERENCIA", arquivo)
    resultado, feitos = montar_dataset.aplicar_correcoes_de_referencia([r])
    assert feitos == 1 and resultado[0]["casos"][0]["esperado"] == "4" and "x * 2" in resultado[0]["referencia"]

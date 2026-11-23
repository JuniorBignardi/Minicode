import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "experiments" / "dataset"))
sys.path.insert(0, str(RAIZ / "experiments" / "gabarito"))

import gerar_tarefas  # noqa: E402

BOA = {
    "nome": "pontos_do_jogo", "arquivo": "jogo.py",
    "pedido": "Crie em jogo.py a função pontos_do_jogo(acertos, erros) que dá 10 pontos por acerto menos 3 por erro, nunca abaixo de zero, e levanta ValueError se algum valor for negativo.",
    "referencia": "def pontos_do_jogo(acertos, erros):\n    if acertos < 0 or erros < 0:\n        raise ValueError('negativo')\n    return max(0, acertos * 10 - erros * 3)\n",
    "entradas": ["pontos_do_jogo(0, 0)", "pontos_do_jogo(1, 0)", "pontos_do_jogo(2, 3)", "pontos_do_jogo(0, 5)",
                 "pontos_do_jogo(5, 1)", "pontos_do_jogo(10, 10)", "pontos_do_jogo(-1, 0)", "pontos_do_jogo(3, 0)"],
}
OUTRA = {
    "nome": "frete_da_encomenda", "arquivo": "loja.py",
    "pedido": "Faça em loja.py a função frete_da_encomenda(peso) que cobra 8 reais até 2 kg e mais 3 reais por kg extra inteiro, e levanta ValueError para peso zero ou negativo.",
    "referencia": "def frete_da_encomenda(peso):\n    if peso <= 0:\n        raise ValueError('peso')\n    return 8 + max(0, int(peso) - 2) * 3\n",
    "entradas": ["frete_da_encomenda(1)", "frete_da_encomenda(2)", "frete_da_encomenda(3)", "frete_da_encomenda(5)",
                 "frete_da_encomenda(10)", "frete_da_encomenda(2.5)", "frete_da_encomenda(0)", "frete_da_encomenda(4)"],
}


def com(base, **mudancas):
    return {**base, **mudancas}


def test_tarefa_boa_guarda_as_saidas_da_execucao_da_referencia():
    saidas, motivo = gerar_tarefas.validar_tarefa(BOA)
    assert motivo == ""
    assert saidas[2] == {"ok": True, "repr": "11"}
    assert saidas[6] == {"ok": False, "excecao": "ValueError"}


def test_referencia_com_erro_de_sintaxe_e_recusada():
    assert gerar_tarefas.validar_tarefa(com(BOA, referencia="def pontos(:\n"))[0] is None


def test_referencia_nao_deterministica_e_recusada():
    ref = "import random\ndef pontos_do_jogo(a, e):\n    return random.random()\n"
    assert gerar_tarefas.validar_tarefa(com(BOA, referencia=ref))[1] == "não determinística"


def test_entrada_que_a_referencia_nao_executa_e_recusada():
    entradas = BOA["entradas"][:-1] + ["pontos_do_jogo(variavel_que_nao_existe, 1)"]
    assert "não executa" in gerar_tarefas.validar_tarefa(com(BOA, entradas=entradas))[1]


def test_saidas_pouco_variadas_sao_recusadas():
    ref = "def pontos_do_jogo(a, e):\n    return 1\n"
    assert "pouco variadas" in gerar_tarefas.validar_tarefa(com(BOA, referencia=ref))[1]


def test_o_pedido_precisa_citar_o_arquivo():
    assert gerar_tarefas.validar_tarefa(com(BOA, pedido="Crie a função pontos_do_jogo."))[0] is None


def test_tarefa_parecida_com_o_benchmark_e_recusada():
    pedido = "Crie uma função fatorial(n) no arquivo fatorial.py. Para n negativo deve levantar ValueError."
    tarefa = com(BOA, nome="fatorial_de", arquivo="fatorial.py", pedido=pedido)
    assert gerar_tarefas.validar_tarefa(tarefa)[1] == "parecida com uma tarefa do benchmark"


def test_nome_igual_ao_de_uma_tarefa_do_benchmark_e_recusado():
    tarefa = com(BOA, nome="validar_senha", pedido="Crie em jogo.py a função validar_senha que pontua o jogo de cartas por rodada.")
    assert gerar_tarefas.validar_tarefa(tarefa)[1] == "nome igual ao de uma tarefa do benchmark"


def test_tarefa_repetida_entre_as_sinteticas_e_recusada():
    assert gerar_tarefas.validar_tarefa(BOA, existentes=[{"nome": "pontos_do_jogo", "pedido": "x"}])[1] == "repete uma tarefa sintética"


def test_gerar_grava_so_as_validas_e_nao_repete(tmp_path):
    respostas = [json.dumps(BOA), json.dumps(BOA), json.dumps(OUTRA)]

    def chat(mensagens, temperature=0, **kw):
        return respostas.pop(0)

    saida = tmp_path / "tarefas.jsonl"
    registros = gerar_tarefas.gerar(chat, lambda esquema, nome: {"nome": nome}, saida, 2, threads=1, log=lambda m: None)

    assert [r["nome"] for r in registros] == ["pontos_do_jogo", "frete_da_encomenda"]
    linhas = [json.loads(l) for l in saida.read_text(encoding="utf-8").splitlines()]
    assert len(linhas) == 2 and linhas[0]["id"] == "s0001" and linhas[1]["saidas"][0]["repr"] == "8"


def test_gerar_para_quando_o_modelo_so_devolve_lixo(tmp_path):
    chamadas = []

    def chat(mensagens, temperature=0, **kw):
        chamadas.append(1)
        return "não é json"

    registros = gerar_tarefas.gerar(chat, lambda esquema, nome: {}, tmp_path / "t.jsonl", 1, threads=1, log=lambda m: None)
    assert registros == [] and len(chamadas) <= 20


def test_normalizar_acerta_a_forma_sem_mexer_no_comportamento():
    bruto = {"nome": "Pontos do Jogo (função)", "arquivo": "Jogo", "pedido": "Pontue o jogo.",
             "referencia": BOA["referencia"], "entradas": ["pontos_do_jogo(1, 0)", "  ", 7, "pontos_do_jogo(2, 0)"]}

    tarefa = gerar_tarefas.normalizar(bruto)

    assert tarefa["nome"] == "pontos_do_jogo" and tarefa["arquivo"] == "jogo.py"
    assert tarefa["pedido"] == "No arquivo jogo.py: Pontue o jogo."
    assert tarefa["entradas"] == ["pontos_do_jogo(1, 0)", "pontos_do_jogo(2, 0)"]
    assert tarefa["referencia"] == BOA["referencia"]


def test_normalizar_mantem_o_pedido_que_ja_cita_o_arquivo():
    tarefa = gerar_tarefas.normalizar(dict(BOA))
    assert tarefa["pedido"] == BOA["pedido"]


def test_entrada_que_nao_chama_o_codigo_e_recusada():
    entradas = BOA["entradas"][:-1] + ["[1, 2, 3]"]
    assert gerar_tarefas.validar_tarefa(com(BOA, entradas=entradas))[1] == "alguma entrada não chama o código"

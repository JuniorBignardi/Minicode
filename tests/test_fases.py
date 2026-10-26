import json

from minicode.agent.maquina.estados import Execucao, FAILED, FERRAMENTAS_POR_ESTADO, IMPLEMENTING, PLANNED, SPECIFIED, VERIFYING
from minicode.agent.conversas.fases import (
    MAX_LEITURAS, TEMPERATURA_POR_FASE, rodar_fase_documento, rodar_fase_implementacao,
)
from minicode.tracing.registro import iniciar_registro

import pytest


def marcar_como_lidos(execucao, raiz):
    # simula que o modelo já leu os arquivos que existem no projeto (o gate de leitura os libera)
    for arquivo in raiz.rglob("*.py"):
        execucao.arquivos_vistos.add(arquivo.relative_to(raiz).as_posix())


def chat_falso(respostas):
    # devolve uma resposta pronta por chamada, na ordem
    fila = list(respostas)

    def chat(mensagens, temperature=0, **kw):
        return fila.pop(0)

    return chat


def acao(tool, **args):
    return json.dumps({"tool": tool, "args": args})


def validar_bom(texto):
    # validador de mentira: só aceita documentos que contenham "bom"
    return ("bom" in texto), "falta a palavra bom"


def preparar(tmp_path, max_iteracoes=30):
    iniciar_registro(tmp_path, "tarefa")
    return Execucao("tarefa", max_iteracoes=max_iteracoes), []


def preparar_implementacao(tmp_path, max_iteracoes=30):
    execucao, mensagens = preparar(tmp_path, max_iteracoes)
    execucao.spec = "spec"
    execucao.mudar_para(SPECIFIED)
    execucao.plano = "plano"
    execucao.mudar_para(PLANNED)
    execucao.mudar_para(IMPLEMENTING)
    return execucao, mensagens


def eventos(tmp_path):
    linhas = (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


# --- fase de documento ---

def test_documento_aceito_de_primeira(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso(["<spec>documento bom</spec>"])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "documento bom"
    assert execucao.chamadas_llm == 1


def test_documento_invalido_volta_para_a_llm_e_ela_reenvia(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso(["<spec>ruim</spec>", "<spec>agora bom</spec>"])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "agora bom"
    assert execucao.chamadas_llm == 2
    assert "falta a palavra bom" in mensagens[-2]["content"]


def test_llm_le_um_arquivo_antes_de_entregar_o_documento(tmp_path):
    (tmp_path / "a.py").write_text("x = 123", encoding="utf-8")
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso([acao("read_file", path="a.py"), "<spec>bom</spec>"])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "bom"
    assert "x = 123" in mensagens[1]["content"]


def test_escrita_e_proibida_na_fase_de_documento(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso([acao("write_file", path="a.py", content="x"), "<spec>bom</spec>"])

    rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert not (tmp_path / "a.py").exists()
    assert "não é permitida" in mensagens[1]["content"]
    assert execucao.arquivos_alterados == []


def test_resposta_sem_formato_valido_volta_para_a_llm(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso(["só conversa", "<spec>bom</spec>"])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "bom"
    assert "Formato inválido" in mensagens[1]["content"]


def test_chamada_repetida_nao_e_executada_de_novo(tmp_path):
    (tmp_path / "a.py").write_text("x = 1", encoding="utf-8")
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso([
        acao("read_file", path="a.py"),
        acao("read_file", path="a.py"),
        "<spec>bom</spec>",
    ])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "bom"
    assert [e["tipo"] for e in eventos(tmp_path)].count("ferramenta") == 1
    assert "já fez esta chamada" in mensagens[3]["content"]


def test_limite_de_leituras_na_fase_de_documento(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    leituras = [acao("read_file", path=f"arquivo{i}.py") for i in range(MAX_LEITURAS + 1)]
    chat = chat_falso(leituras + ["<spec>bom</spec>"])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "bom"
    assert [e["tipo"] for e in eventos(tmp_path)].count("ferramenta") == MAX_LEITURAS
    assert "Limite" in mensagens[-2]["content"]


def test_cada_fase_usa_a_sua_temperatura(tmp_path):
    usadas = []

    def chat(mensagens, temperature=0, **kw):
        usadas.append(temperature)
        return "<spec>bom</spec>"

    execucao, mensagens = preparar(tmp_path)
    rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert usadas == [TEMPERATURA_POR_FASE["spec"]]


def test_formato_invalido_guarda_a_resposta_completa_no_registro(tmp_path):
    execucao, mensagens = preparar(tmp_path)
    resposta_longa = "texto sem formato " * 40
    chat = chat_falso([resposta_longa, "<spec>bom</spec>"])

    rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    invalidos = [e for e in eventos(tmp_path) if e["tipo"] == "formato_invalido"]
    assert invalidos[0]["resposta_completa"] == resposta_longa


def test_erro_de_rede_na_llm_leva_a_failed_com_o_erro_registrado(tmp_path):
    def chat_com_timeout(mensagens, temperature=0, **kw):
        raise TimeoutError("sem resposta")

    execucao, mensagens = preparar(tmp_path)

    doc = rodar_fase_documento(execucao, chat_com_timeout, mensagens, tmp_path, "spec", validar_bom)

    assert doc is None
    assert execucao.estado == FAILED
    erros = [e for e in eventos(tmp_path) if e["tipo"] == "erro_llm"]
    assert "TimeoutError" in erros[0]["erro"]


def test_erro_de_rede_na_implementacao_devolve_false(tmp_path):
    def chat_com_erro(mensagens, temperature=0, **kw):
        raise ConnectionError("rede fora do ar")

    execucao, mensagens = preparar_implementacao(tmp_path)

    assert rodar_fase_implementacao(execucao, chat_com_erro, mensagens, tmp_path) is False
    assert execucao.estado == FAILED


def test_limite_de_iteracoes_na_fase_de_documento(tmp_path):
    execucao, mensagens = preparar(tmp_path, max_iteracoes=2)
    chat = chat_falso(["conversa"] * 5)

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc is None
    assert execucao.estado == FAILED
    assert execucao.chamadas_llm == 2


# --- fase de implementação ---

def test_escreve_arquivo_e_finish_aceito(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([acao("write_file", path="a.py", content="x = 1\n"), acao("finish")])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert execucao.estado == VERIFYING
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 1\n"
    assert execucao.arquivos_alterados == ["a.py"]


def test_finish_sem_escrita_e_recusado_e_depois_aceito(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("finish"),
        acao("write_file", path="a.py", content="x = 1\n"),
        acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert "finish recusado" in mensagens[1]["content"]
    assert execucao.chamadas_llm == 3


def test_ferramenta_inexistente_volta_como_erro(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("apagar_tudo"),
        acao("write_file", path="a.py", content="x"),
        acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert "não é permitida" in mensagens[1]["content"]


def test_argumentos_com_nome_errado_nao_quebram_o_agente(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("write_file", caminho="a.py", texto="x"),
        acao("write_file", path="a.py", content="x"),
        acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert "argumentos inválidos" in mensagens[1]["content"]


def test_caminho_fora_do_projeto_volta_como_erro(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("write_file", path="../fora.txt", content="x"),
        acao("write_file", path="a.py", content="x"),
        acao("finish"),
    ])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert not (tmp_path.parent / "fora.txt").exists()
    assert "fora do projeto" in mensagens[1]["content"]
    assert execucao.arquivos_alterados == ["a.py"]


def test_teste_protegido_nao_pode_ser_sobrescrito(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("original", encoding="utf-8")
    execucao, mensagens = preparar_implementacao(tmp_path)
    execucao.arquivos_protegidos = ["tests/test_a.py"]
    chat = chat_falso([
        acao("write_file", path="tests/test_a.py", content="enfraquecido"),
        acao("write_file", path="b.py", content="x"),
        acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert (tmp_path / "tests" / "test_a.py").read_text(encoding="utf-8") == "original"
    assert "protegido" in mensagens[1]["content"] or "não pode ser alterado" in mensagens[1]["content"]
    assert execucao.arquivos_alterados == ["b.py"]


def test_limite_de_iteracoes_na_implementacao(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path, max_iteracoes=2)
    chat = chat_falso([acao("list_files")] * 5)

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is False
    assert execucao.estado == FAILED


# --- schema da resposta (response_format) ---

def test_implementacao_pede_resposta_no_formato_do_schema_com_as_ferramentas_do_estado(tmp_path):
    recebidos = []
    fila = [acao("finish")]

    def chat(mensagens, temperature=0, **kw):
        recebidos.append(kw)
        return fila.pop(0)

    execucao, mensagens = preparar_implementacao(tmp_path)
    execucao.registrar_escrita("a.py")

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    esquema = recebidos[0]["response_format"]["json_schema"]["schema"]
    assert esquema["properties"]["tool"]["enum"] == FERRAMENTAS_POR_ESTADO[IMPLEMENTING]


def test_fases_de_documento_nao_usam_schema(tmp_path):
    recebidos = []

    def chat(mensagens, temperature=0, **kw):
        recebidos.append(kw)
        return "<spec>bom</spec>"

    execucao, mensagens = preparar(tmp_path)
    rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert recebidos == [{}]


# --- conteúdo com "\n" literais ---

def test_codigo_gravado_com_barra_n_literal_e_desescapado(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    literal = "class Pilha:\\n    def __init__(self):\\n        self.itens = []\\n"   # barra + n, sem quebra real
    chat = chat_falso([acao("write_file", path="pilha.py", content=literal), acao("finish")])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    gravado = (tmp_path / "pilha.py").read_text(encoding="utf-8")
    assert gravado == "class Pilha:\n    def __init__(self):\n        self.itens = []\n"
    compile(gravado, "pilha.py", "exec")   # agora é Python válido
    assert "conteudo_desescapado" in [e["tipo"] for e in eventos(tmp_path)]


def test_codigo_com_quebras_reais_nao_e_alterado(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    original = 'print("a\\nb")\nx = 1\n'   # tem quebra real e um \n dentro de uma string
    chat = chat_falso([acao("write_file", path="a.py", content=original), acao("finish")])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert (tmp_path / "a.py").read_text(encoding="utf-8") == original
    assert "conteudo_desescapado" not in [e["tipo"] for e in eventos(tmp_path)]


def test_uma_linha_com_um_unico_barra_n_nao_e_alterada(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    linha = 'print("a\\nb")'    # uma só linha, um só \n legítimo
    chat = chat_falso([acao("write_file", path="a.py", content=linha), acao("finish")])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert (tmp_path / "a.py").read_text(encoding="utf-8") == linha


def test_arquivo_que_nao_e_python_nao_e_desescapado(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    texto = "linha1\\nlinha2\\nlinha3"
    chat = chat_falso([acao("write_file", path="a.txt", content=texto), acao("finish")])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert (tmp_path / "a.txt").read_text(encoding="utf-8") == texto


# --- várias ações na mesma resposta ---

def test_varias_acoes_na_mesma_resposta_sao_executadas_em_ordem(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("write_file", path="a.py", content="x = 1\n") + "\n"
        + acao("write_file", path="b.py", content="y = 2\n") + "\n"
        + acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert execucao.arquivos_alterados == ["a.py", "b.py"]
    assert execucao.chamadas_llm == 1


def test_finish_antes_da_escrita_na_mesma_resposta_e_recusado(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([
        acao("finish") + "\n" + acao("write_file", path="a.py", content="x = 1\n"),
        acao("finish"),
    ])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert "finish recusado" in mensagens[1]["content"]
    assert execucao.arquivos_alterados == ["a.py"]


def test_varias_leituras_na_fase_de_documento(tmp_path):
    (tmp_path / "a.py").write_text("AAA", encoding="utf-8")
    (tmp_path / "b.py").write_text("BBB", encoding="utf-8")
    execucao, mensagens = preparar(tmp_path)
    chat = chat_falso([
        acao("read_file", path="a.py") + "\n" + acao("read_file", path="b.py"),
        "<spec>bom</spec>",
    ])

    doc = rodar_fase_documento(execucao, chat, mensagens, tmp_path, "spec", validar_bom)

    assert doc == "bom"
    assert "AAA" in mensagens[1]["content"]
    assert "BBB" in mensagens[1]["content"]


def test_json_com_aspas_faltando_e_consertado_e_executado(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    quebrado = '{"tool": "write_file", "args": {"path": "a.py", "content": "x = 1}}'
    chat = chat_falso([quebrado, acao("finish")])

    terminou = rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert terminou is True
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 1"
    assert "json_reparado" in [e["tipo"] for e in eventos(tmp_path)]


def test_formato_invalido_diz_qual_e_o_erro_do_json(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    cortado = '{"tool": "write_file", "args": {"path": "a.py", "content": "def f():\\n    ret'
    chat = chat_falso([cortado, acao("write_file", path="a.py", content="x"), acao("finish")])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    assert "Unterminated string" in mensagens[1]["content"]
    invalidos = [e for e in eventos(tmp_path) if e["tipo"] == "formato_invalido"]
    assert "Unterminated string" in invalidos[0]["motivo"]


# --- registro ---

def test_fases_registram_o_que_aconteceu(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    chat = chat_falso([acao("write_file", path="a.py", content="x = 1\n"), acao("finish")])

    rodar_fase_implementacao(execucao, chat, mensagens, tmp_path)

    tipos = [e["tipo"] for e in eventos(tmp_path)]
    assert tipos.count("chamada_llm") == 2
    assert "ferramenta" in tipos
    assert "finish_aceito" in tipos


# --- o teste que falhou precisa mudar (depois de um diagnóstico TEST_BUG) ---

ARQUIVO_DE_TESTE = "def test_a():\n    assert 1 == 2\n\n\ndef test_b():\n    assert 1 == 1\n"


def preparar_reparo_de_teste(tmp_path, restricao="testes"):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(ARQUIVO_DE_TESTE, encoding="utf-8")
    execucao.restricao_escrita = restricao
    execucao.testes_que_falharam = ["test_a"]
    marcar_como_lidos(execucao, tmp_path)
    return execucao, executar_acao


def escrever_teste(executar_acao, execucao, tmp_path, conteudo):
    return executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "tests/test_x.py", "content": conteudo}})


def test_reescrever_o_teste_que_falhou_sem_mudar_nada_e_recusado(tmp_path):
    execucao, executar_acao = preparar_reparo_de_teste(tmp_path)

    ok, texto = escrever_teste(executar_acao, execucao, tmp_path, ARQUIVO_DE_TESTE + "\n\ndef test_c():\n    pass\n")

    assert ok is False
    assert "NÃO foi gravado" in texto and "test_a" in texto
    assert (tmp_path / "tests" / "test_x.py").read_text(encoding="utf-8") == ARQUIVO_DE_TESTE
    assert "escrita_sem_mudanca" in [e["tipo"] for e in eventos(tmp_path)]


def test_alterar_o_teste_que_falhou_e_aceito(tmp_path):
    execucao, executar_acao = preparar_reparo_de_teste(tmp_path)
    novo = ARQUIVO_DE_TESTE.replace("1 == 2", "2 == 2")

    ok, texto = escrever_teste(executar_acao, execucao, tmp_path, novo)

    assert ok is True
    assert (tmp_path / "tests" / "test_x.py").read_text(encoding="utf-8") == novo


def test_remover_o_teste_que_falhou_conta_como_mudanca(tmp_path):
    execucao, executar_acao = preparar_reparo_de_teste(tmp_path)

    ok, texto = escrever_teste(executar_acao, execucao, tmp_path, "def test_b():\n    assert 1 == 1\n")

    assert ok is True


def test_sem_restricao_de_teste_a_regra_nao_se_aplica(tmp_path):
    execucao, executar_acao = preparar_reparo_de_teste(tmp_path, restricao=None)

    ok, texto = escrever_teste(executar_acao, execucao, tmp_path, ARQUIVO_DE_TESTE + "\n\ndef test_c():\n    pass\n")

    assert ok is True


def test_arquivo_novo_nao_e_afetado_pela_regra(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    execucao.restricao_escrita = "testes"
    execucao.testes_que_falharam = ["test_a"]

    ok, texto = executar_acao(execucao, tmp_path,
                              {"tool": "write_file", "args": {"path": "tests/test_novo.py", "content": "def test_n():\n    pass\n"}})

    assert ok is True


def test_o_modelo_que_insiste_no_mesmo_teste_deixa_de_ser_recusado_depois_de_duas_vezes(tmp_path):
    execucao, executar_acao = preparar_reparo_de_teste(tmp_path)
    mesmo = ARQUIVO_DE_TESTE + "\n\ndef test_c():\n    pass\n"

    resultados = [escrever_teste(executar_acao, execucao, tmp_path, mesmo)[0] for _ in range(3)]

    assert resultados == [False, False, True]     # a 3ª tentativa passa: a restrição foi levantada
    assert execucao.restricao_escrita is None


# --- temperatura por fase ---

def test_cada_chamada_usa_a_temperatura_fixa_da_fase(tmp_path):
    from minicode.agent.conversas.fases import TEMPERATURA_POR_FASE, pedir_resposta
    execucao, mensagens = preparar_implementacao(tmp_path)
    execucao.tentativas = 3   # o reparo não muda a temperatura
    usadas = []

    def chat(mensagens, temperature=0, **kw):
        usadas.append(temperature)
        return "{}"

    for fase in ("spec", "implementacao", "revisao"):
        pedir_resposta(execucao, chat, mensagens, tmp_path, fase)

    assert usadas == [TEMPERATURA_POR_FASE[f] for f in ("spec", "implementacao", "revisao")]


# --- remoção dos testes que falharam (diagnóstico TEST_BUG) ---

def test_remover_testes_que_falharam_apaga_so_a_funcao_que_falhou(tmp_path):
    from minicode.agent.gates.escrita import remover_testes_que_falharam
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(
        "def test_a():\n    assert 1 == 1\n\n\n@pytest.mark.slow\ndef test_b():\n    assert 1 == 2\n\n\ndef test_c():\n    assert 2 == 2\n",
        encoding="utf-8")
    execucao.arquivos_alterados = ["tests/test_x.py"]
    execucao.testes_que_falharam = ["test_b"]

    removidos = remover_testes_que_falharam(execucao, tmp_path)

    assert removidos == [("tests/test_x.py", "test_b")]
    texto = (tmp_path / "tests" / "test_x.py").read_text(encoding="utf-8")
    assert "test_a" in texto and "test_c" in texto
    assert "test_b" not in texto and "slow" not in texto


def test_remover_nao_toca_em_codigo_nem_em_teste_protegido(tmp_path):
    from minicode.agent.gates.escrita import remover_testes_que_falharam
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_b():\n    assert 1 == 2\n", encoding="utf-8")
    (tmp_path / "test_b_codigo.py").write_text("def test_b():\n    pass\n", encoding="utf-8")
    execucao.arquivos_alterados = ["tests/test_x.py"]
    execucao.arquivos_protegidos = ["tests/test_x.py"]
    execucao.testes_que_falharam = ["test_b"]

    assert remover_testes_que_falharam(execucao, tmp_path) == []
    assert "test_b" in (tmp_path / "tests" / "test_x.py").read_text(encoding="utf-8")


# --- escrita que deixaria o Python inválido ---

def test_problema_no_python_acha_sintaxe_e_codigo_inalcancavel():
    from minicode.agent.gates.escrita import problema_no_python
    assert problema_no_python("x = 1\n") is None
    assert "sintaxe" in problema_no_python("def f(:\n    pass\n")
    assert "inalcançável" in problema_no_python("def f():\n    return 1\n    x = 2\n")
    assert "inalcançável" in problema_no_python("for i in x:\n    if i:\n        break\n        y = 1\n")


def test_write_file_com_sintaxe_quebrada_e_recusado(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": "def f(:\n"}})

    assert ok is False and "sintaxe" in texto
    assert not (tmp_path / "a.py").exists()


def test_arquivos_que_nao_sao_python_nao_sao_checados(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.txt", "content": "def f(:\n"}})

    assert ok is True


def test_write_file_que_deixa_codigo_depois_do_return_e_recusado(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    conteudo = "def f():\n    return 1\n    x = 2\n"

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": conteudo}})

    assert ok is False and "inalcançável" in texto
    assert not (tmp_path / "a.py").exists()


def test_arquivo_ja_quebrado_pode_ser_regravado_em_etapas(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "a.py").write_text("def f(:\n    x = (\n", encoding="utf-8")
    conteudo = "def f():\n    x = (\n"   # continua quebrado: a escrita não cria um problema novo

    marcar_como_lidos(execucao, tmp_path)
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": conteudo}})

    assert ok is True


# --- sobrescrever um arquivo de teste não apaga testes ---

DOIS_TESTES = "def test_a():\n    assert 1 == 1\n\n\ndef test_b():\n    assert 2 == 2\n"


def preparar_arquivo_de_teste(tmp_path):
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(DOIS_TESTES, encoding="utf-8")
    return execucao


def test_sobrescrever_arquivo_de_teste_apagando_um_teste_e_recusado(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao = preparar_arquivo_de_teste(tmp_path)
    conteudo = "def test_a():\n    assert 1 == 1\n"

    marcar_como_lidos(execucao, tmp_path)
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "tests/test_x.py", "content": conteudo}})

    assert ok is False and "test_b" in texto
    assert (tmp_path / "tests" / "test_x.py").read_text(encoding="utf-8") == DOIS_TESTES


def test_sobrescrever_mantendo_ou_acrescentando_testes_e_aceito(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao = preparar_arquivo_de_teste(tmp_path)
    conteudo = DOIS_TESTES + "\n\ndef test_c():\n    assert 3 == 3\n"

    marcar_como_lidos(execucao, tmp_path)
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "tests/test_x.py", "content": conteudo}})

    assert ok is True


def test_o_teste_que_acabou_de_falhar_pode_ser_retirado(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao = preparar_arquivo_de_teste(tmp_path)
    execucao.testes_que_falharam = ["test_b"]
    conteudo = "def test_a():\n    assert 1 == 1\n"

    marcar_como_lidos(execucao, tmp_path)
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "tests/test_x.py", "content": conteudo}})

    assert ok is True


def test_create_file_passa_pelos_mesmos_gates_de_escrita(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "create_file", "args": {"path": "a.py", "content": "def f(:\n"}})
    assert ok is False and "sintaxe" in texto

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "create_file", "args": {"path": "a.py", "content": "x = 1\n"}})
    assert ok is True and execucao.arquivos_alterados == ["a.py"]


# --- search_code e git_diff no agente ---

def test_search_code_esta_disponivel_para_ler_e_git_diff_so_na_implementacao():
    from minicode.agent.maquina.estados import RECEIVED
    assert "search_code" in FERRAMENTAS_POR_ESTADO[RECEIVED]
    assert "search_code" in FERRAMENTAS_POR_ESTADO[IMPLEMENTING]
    assert "git_diff" not in FERRAMENTAS_POR_ESTADO[RECEIVED]
    assert "git_diff" in FERRAMENTAS_POR_ESTADO[IMPLEMENTING]


def test_o_agente_executa_search_code(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "a.py").write_text("def soma(a, b):\n    return a + b\n", encoding="utf-8")

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "search_code", "args": {"padrao": "soma"}})

    assert ok is True and texto == "a.py:1: def soma(a, b):"


# --- o conteúdo original dos arquivos é guardado antes da primeira alteração ---

def test_a_primeira_escrita_guarda_o_conteudo_original(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")

    marcar_como_lidos(execucao, tmp_path)
    executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": "x = 2\n"}})
    executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": "x = 3\n"}})

    # fica o original, não a versão intermediária
    assert execucao.originais == {"a.py": "x = 1\n"}


def test_arquivo_novo_nao_tem_original(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)

    executar_acao(execucao, tmp_path, {"tool": "create_file", "args": {"path": "novo.py", "content": "x = 1\n"}})

    assert execucao.originais == {}


def test_o_diff_mostra_o_que_mudou_em_relacao_ao_original(tmp_path):
    from minicode.agent.gates.escrita import diferenca_dos_originais
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "a.py").write_text("def f():\n    return 110.0\n", encoding="utf-8")

    assert diferenca_dos_originais(execucao, tmp_path) == ""   # ainda não mudou nada

    marcar_como_lidos(execucao, tmp_path)
    executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "a.py", "content": "def f():\n    return 100.1\n"}})
    diff = diferenca_dos_originais(execucao, tmp_path)

    assert "-    return 110.0" in diff and "+    return 100.1" in diff
    assert "a.py (original)" in diff


# --- ler antes de sobrescrever ---

def test_sobrescrever_arquivo_existente_sem_te_lo_lido_e_recusado(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "servico.py").write_text("class Servico:\n    def criar_usuario(self):\n        pass\n", encoding="utf-8")

    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "servico.py", "content": "class Servico:\n    pass\n"}})

    assert ok is False and "read_file" in texto and "servico.py" in texto
    assert "criar_usuario" in (tmp_path / "servico.py").read_text(encoding="utf-8")   # nada foi apagado


def test_depois_de_ler_o_arquivo_pode_sobrescreve_lo(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    (tmp_path / "servico.py").write_text("x = 1\n", encoding="utf-8")

    executar_acao(execucao, tmp_path, {"tool": "read_file", "args": {"path": "servico.py"}})
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "servico.py", "content": "x = 2\n"}})

    assert ok is True


def test_arquivo_que_o_proprio_agente_criou_nao_precisa_ser_relido(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)

    executar_acao(execucao, tmp_path, {"tool": "create_file", "args": {"path": "novo.py", "content": "x = 1\n"}})
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "novo.py", "content": "x = 2\n"}})

    assert ok is True


def test_arquivo_novo_nao_exige_leitura(tmp_path):
    from minicode.agent.conversas.fases import executar_acao
    execucao, mensagens = preparar_implementacao(tmp_path)
    ok, texto = executar_acao(execucao, tmp_path, {"tool": "write_file", "args": {"path": "outro.py", "content": "x = 1\n"}})
    assert ok is True

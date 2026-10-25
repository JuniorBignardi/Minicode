import json

from minicode.agent.estados import DONE, FAILED
from minicode.agent.orquestrador import rodar_agente

REVISAO_APROVADA = json.dumps({"criterios": [{"criterio": "x", "atendido": True, "motivo": "ok"}]})


PLANO_DE_TESTES_APROVADO = json.dumps({"casos": [{"caso": "x", "esperado_correto": True, "motivo": "ok"}]})
SPEC_COBERTA = json.dumps({"requisitos": [{"requisito": "x", "coberto": True, "motivo": "ok"}]})
DIAGNOSTICO_DESCONHECIDO = json.dumps({"classificacao": "UNKNOWN", "evidencias": "e", "proxima_acao": "p"})


def nome_do_schema(kw):
    return kw.get("response_format", {}).get("json_schema", {}).get("name")


def e_revisao(kw):
    # as revisões do código e dos testes usam o schema "revisao"
    return nome_do_schema(kw) == "revisao"


def resposta_automatica(kw):
    # chamadas que a maioria dos testes não quer controlar: revisão da spec e diagnóstico
    nome = nome_do_schema(kw)
    if nome == "revisao":
        return REVISAO_APROVADA
    if nome == "revisao_spec":
        return SPEC_COBERTA
    if nome == "diagnostico":
        return DIAGNOSTICO_DESCONHECIDO
    if nome == "plano_de_testes":
        # um caso para cada critério que o schema aceita
        criterios = kw["response_format"]["json_schema"]["schema"]["properties"]["casos"]["items"]["properties"]["criterio"]["enum"]
        return json.dumps({"casos": [{"criterio": c, "entrada": "i", "esperado": "e"} for c in criterios]})
    if nome == "revisao_plano_de_testes":
        return PLANO_DE_TESTES_APROVADO
    return None


SPEC = """<spec>
# Specification

## Objective
Criar a função fatorial.

## Acceptance Criteria
- fatorial(0) == 1
- fatorial(5) == 120
</spec>"""

PLANO = """<plan>
1. criar fat.py com a função
2. criar testes
</plan>"""

FATORIAL_CERTO = "def fatorial(n):\n    if n == 0:\n        return 1\n    return n * fatorial(n - 1)\n"
FATORIAL_ERRADO = "def fatorial(n):\n    return n\n"

TESTES = (
    "from fat import fatorial\n\n"
    "def test_zero():\n    assert fatorial(0) == 1\n\n"
    "def test_cinco():\n    assert fatorial(5) == 120\n"
)


def chat_falso(respostas):
    fila = list(respostas)

    def chat(mensagens, temperature=0, **kw):
        automatica = resposta_automatica(kw)
        if automatica is not None:
            return automatica
        return fila.pop(0)

    return chat


def acao(tool, **args):
    return json.dumps({"tool": tool, "args": args})


def escrever(path, content):
    return acao("write_file", path=path, content=content)


def estado_salvo(raiz):
    return json.loads((raiz / ".minicode" / "state.json").read_text(encoding="utf-8"))


def eventos(raiz):
    linhas = (raiz / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


def test_caminho_feliz(tmp_path):
    chat = chat_falso([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_CERTO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert execucao.tentativas == 0
    assert execucao.testes_passaram is True
    assert execucao.chamadas_llm == 10   # 5 + revisão da spec + plano de testes + revisão dele + revisão do código + revisão dos testes

    registro = tmp_path / ".minicode"
    assert "fatorial" in (registro / "specification.md").read_text(encoding="utf-8")
    assert "criar fat.py" in (registro / "plan.md").read_text(encoding="utf-8")
    assert estado_salvo(tmp_path)["estado"] == "DONE"

    tipos = [e["tipo"] for e in eventos(tmp_path)]
    assert "testes" in tipos
    assert tipos[-1] == "resultado_final"


def test_reparo_depois_de_testes_falharem(tmp_path):
    chat = chat_falso([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_ERRADO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),                         # testes falham
        escrever("fat.py", FATORIAL_CERTO),     # reparo
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert execucao.tentativas == 1
    assert (tmp_path / "fat.py").read_text(encoding="utf-8") == FATORIAL_CERTO


def test_a_llm_recebe_a_saida_dos_testes_no_reparo(tmp_path):
    historicos = []

    respostas = [
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_ERRADO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),
        escrever("fat.py", FATORIAL_CERTO),
        acao("finish"),
    ]
    fila = list(respostas)

    def chat(mensagens, temperature=0, **kw):
        automatica = resposta_automatica(kw)
        if automatica is not None:
            return automatica
        historicos.append(list(mensagens))
        return fila.pop(0)

    rodar_agente("crie fatorial", tmp_path, chat)

    ultima_chamada = historicos[-1]
    mensagens_de_usuario = [m["content"] for m in ultima_chamada if m["role"] == "user"]
    assert any("Os testes falharam" in texto for texto in mensagens_de_usuario)

    # o reparo traz a especificação e o diagnóstico "teste ou código?"
    reparo = [t for t in mensagens_de_usuario if "Os testes falharam" in t][0]
    assert "fatorial(5) == 120" in reparo
    assert "CONTRADIZ a especificação" in reparo


def test_esgotar_as_tentativas_leva_a_failed(tmp_path):
    chat = chat_falso([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_ERRADO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),
        acao("finish"),
        acao("finish"),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_tentativas=3)

    assert execucao.estado == FAILED
    assert execucao.tentativas == 3
    assert execucao.testes_passaram is False
    assert estado_salvo(tmp_path)["estado"] == "FAILED"


def test_sem_nenhum_teste_nao_chega_a_done(tmp_path):
    chat = chat_falso([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_CERTO),
        acao("finish"),
        acao("finish"),
        acao("finish"),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == FAILED
    assert execucao.testes_passaram is False


def test_spec_que_nunca_fica_valida_leva_a_failed(tmp_path):
    chat = chat_falso(["só conversa"] * 5)

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_iteracoes=3)

    assert execucao.estado == FAILED
    assert execucao.spec is None
    assert not (tmp_path / ".minicode" / "plan.md").exists()
    assert estado_salvo(tmp_path)["estado"] == "FAILED"


def chat_gravador(respostas):
    # como chat_falso, mas guarda o histórico recebido em cada chamada
    fila = list(respostas)
    historicos = []

    def chat(mensagens, temperature=0, **kw):
        automatica = resposta_automatica(kw)
        if automatica is not None:
            return automatica
        historicos.append(list(mensagens))
        return fila.pop(0)

    return chat, historicos


def test_arquivo_citado_na_tarefa_criado_no_lugar_errado_e_recusado(tmp_path):
    chat, historicos = chat_gravador([
        SPEC, PLANO,
        escrever("pasta/fat.py", FATORIAL_CERTO),     # caminho errado
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),                               # recusado: fat.py não existe na raiz
        escrever("fat.py", FATORIAL_CERTO),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial no arquivo fat.py", tmp_path, chat)

    assert execucao.estado == DONE
    assert "finish_recusado" in [e["tipo"] for e in eventos(tmp_path)]
    ultimo_historico = historicos[-1]
    assert any("citado na tarefa" in m["content"] for m in ultimo_historico if m["role"] == "user")


def test_resultado_identico_dos_testes_gera_aviso_no_reparo(tmp_path):
    chat, historicos = chat_gravador([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_ERRADO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),                               # falha 1
        acao("finish"),                               # falha 2, idêntica à 1
        escrever("fat.py", FATORIAL_CERTO),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    mensagens_antes_do_conserto = historicos[-2]
    assert any("IDÊNTICO" in m["content"] for m in mensagens_antes_do_conserto if m["role"] == "user")
    assert "reparo_sem_progresso" in [e["tipo"] for e in eventos(tmp_path)]


def test_na_ultima_tentativa_a_conversa_recomeca_so_com_o_essencial(tmp_path):
    chat, historicos = chat_gravador([
        SPEC, PLANO,
        escrever("fat.py", FATORIAL_ERRADO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),                               # falha 1
        acao("finish"),                               # falha 2: última tentativa permitida
        escrever("fat.py", FATORIAL_CERTO),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_tentativas=2)

    assert execucao.estado == DONE
    recomeco = historicos[6]                          # chamada logo depois do reinício
    assert [m["role"] for m in recomeco] == ["system", "user"]
    assert "Estado atual dos arquivos" in recomeco[1]["content"]
    assert "def fatorial" in recomeco[1]["content"]
    assert "contexto_reiniciado" in [e["tipo"] for e in eventos(tmp_path)]


def revisao(aprovada, motivo="motivo"):
    return json.dumps({"criterios": [{"criterio": "fatorial(5) == 120", "atendido": aprovada, "motivo": motivo}]})


def chat_com_revisoes(respostas, revisoes):
    # as chamadas de revisão consomem a fila "revisoes"; as demais consomem "respostas"
    fila = list(respostas)
    fila_revisoes = list(revisoes)
    historicos = []

    def chat(mensagens, temperature=0, **kw):
        if e_revisao(kw):
            historicos.append(("revisao", list(mensagens)))
            return fila_revisoes.pop(0)
        if nome_do_schema(kw) in ("revisao_spec", "diagnostico", "plano_de_testes", "revisao_plano_de_testes"):
            return resposta_automatica(kw)
        historicos.append(("agente", list(mensagens)))
        return fila.pop(0)

    return chat, historicos


def eventos_do_registro(tmp_path):
    linhas = (tmp_path / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(linha) for linha in linhas]


def test_revisao_do_codigo_reprova_antes_de_rodar_os_testes(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),                              # revisão do código reprova: testes NEM rodam
         escrever("fat.py", FATORIAL_CERTO),
         acao("finish")],
        [revisao(False, "devolve n em vez do fatorial"),   # código, 1ª vez
         revisao(True),                                    # código, 2ª vez
         revisao(True)],                                   # testes
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert execucao.tentativas == 1
    eventos = eventos_do_registro(tmp_path)
    assert [e["tipo"] for e in eventos].count("testes") == 1          # só rodou depois do conserto
    revisoes = [(e["revisao"], e["aprovada"]) for e in eventos if e["tipo"] == "revisao" and e["revisao"] in ("codigo", "testes")]
    assert revisoes == [("codigo", False), ("codigo", True), ("testes", True)]

    # a LLM recebeu o relatório da revisão para consertar
    ultimo_historico_do_agente = [ms for papel, ms in historicos if papel == "agente"][-1]
    mensagens_de_usuario = [m["content"] for m in ultimo_historico_do_agente if m["role"] == "user"]
    reparo = [t for t in mensagens_de_usuario if "devolve n em vez do fatorial" in t]
    assert reparo, "o relatório da revisão deveria ter chegado à LLM"
    assert "NÃO ATENDIDO" in reparo[0]


TESTE_ERRADO = "from fat import fatorial\n\ndef test_cinco():\n    assert fatorial(5) == 121\n"


def test_codigo_aprovado_pela_revisao_e_testes_falhando_avisa_que_o_erro_esta_nos_testes(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),                              # código aprovado, teste errado falha
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        [revisao(True), revisao(True), revisao(True)],  # código, código, testes
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, diagnosticar=False)

    assert execucao.estado == DONE
    ultimo = [ms for papel, ms in historicos if papel == "agente"][-1]
    avisos = [m["content"] for m in ultimo if m["role"] == "user" and "APROVOU o código" in m["content"]]
    assert avisos, "o reparo deveria dizer que o revisor aprovou o código"
    assert "dica_codigo_aprovado" in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_sem_revisao_nao_ha_aviso_de_codigo_aprovado(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        [],
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, revisar_spec=False)

    assert execucao.estado == DONE
    assert "dica_codigo_aprovado" not in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_revisao_dos_testes_reprova_depois_que_eles_passam(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", "from fat import fatorial\n\ndef test_zero():\n    assert fatorial(0) == 1\n"),
         acao("finish"),                              # testes passam, mas cobrem só um critério
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        [revisao(True),                                    # código, 1ª vez
         revisao(False, "nenhum teste verifica fatorial(5)"),  # testes, 1ª vez
         revisao(True),                                    # código, 2ª vez
         revisao(True)],                                   # testes, 2ª vez
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert execucao.tentativas == 1
    eventos = eventos_do_registro(tmp_path)
    assert [e["tipo"] for e in eventos].count("testes") == 2
    revisoes = [(e["revisao"], e["aprovada"]) for e in eventos if e["tipo"] == "revisao" and e["revisao"] in ("codigo", "testes")]
    assert revisoes == [("codigo", True), ("testes", False), ("codigo", True), ("testes", True)]


def reprova_criterio(numero):
    return json.dumps({"criterios": [{"criterio": f"criterio {numero}", "atendido": False, "motivo": "não cumpre"}]})


def test_reprovacoes_diferentes_a_cada_vez_nunca_chegam_a_done(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"), acao("finish"), acao("finish"), acao("finish")],
        [reprova_criterio(i) for i in range(4)],
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_tentativas=3)

    assert execucao.estado == FAILED
    assert execucao.tentativas == 3
    # os testes nunca chegaram a rodar: a revisão do código reprovou todas as vezes
    assert "testes" not in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_reprovacao_repetida_depois_de_um_reparo_e_dispensada(tmp_path):
    # a revisão pede de novo o mesmo critério: o reparo não consegue dá-lo, então os testes decidem
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),
         escrever("fat.py", FATORIAL_CERTO),
         acao("finish")],
        [reprova_criterio(1), reprova_criterio(1), revisao(True)],   # código, código (repetida), testes
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert execucao.tentativas == 1
    dispensada = [e for e in eventos_do_registro(tmp_path) if e["tipo"] == "revisao_dispensada"]
    assert dispensada and dispensada[0]["revisao"] == "codigo"
    assert "testes" in [e["tipo"] for e in eventos_do_registro(tmp_path)]   # os testes rodaram


def test_revisao_inconclusiva_nao_bloqueia(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        ["isto não é json", "nem isto"],
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert "revisao_inconclusiva" in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_com_a_revisao_desligada_nenhuma_chamada_de_revisao_acontece(tmp_path):
    chat, historicos = chat_com_revisoes(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        [],
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, revisar_spec=False)

    assert execucao.estado == DONE
    assert execucao.chamadas_llm == 6   # 5 + plano de testes (sem a revisão dele)
    assert all(papel == "agente" for papel, _ in historicos)


def test_teste_que_ja_existia_nao_e_sobrescrito(tmp_path):
    (tmp_path / "tests").mkdir()
    original = "def test_antigo():\n    assert True\n"
    (tmp_path / "tests" / "test_antigo.py").write_text(original, encoding="utf-8")

    chat = chat_falso([
        SPEC, PLANO,
        escrever("tests/test_antigo.py", "def test_antigo():\n    assert 1 == 1\n"),  # recusado
        escrever("fat.py", FATORIAL_CERTO),
        escrever("tests/test_fat.py", TESTES),
        acao("finish"),
    ])

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert (tmp_path / "tests" / "test_antigo.py").read_text(encoding="utf-8") == original
    assert "tests/test_antigo.py" not in execucao.arquivos_alterados
    assert "escrita_protegida" in [e["tipo"] for e in eventos(tmp_path)]


# --- revisão da spec contra o pedido ---

def spec_revisada(coberto, motivo="motivo"):
    return json.dumps({"requisitos": [{"requisito": "devolve uma lista", "coberto": coberto, "motivo": motivo}]})


SPEC_TEXTO = """<spec>
# Specification

## Objective
Criar a função fatorial que devolve uma string.

## Acceptance Criteria
- fatorial(5) devolve a string 120
- fatorial(0) devolve a string 1
</spec>"""


def chat_scriptado(respostas, por_schema):
    # respostas: fila do agente; por_schema: nome do schema -> fila de respostas dessa chamada
    fila = list(respostas)
    filas = {nome: list(v) for nome, v in por_schema.items()}
    historicos = []

    def chat(mensagens, temperature=0, **kw):
        nome = nome_do_schema(kw)
        if nome in filas and filas[nome]:
            historicos.append((nome, list(mensagens)))
            return filas[nome].pop(0)
        automatica = resposta_automatica(kw)
        if automatica is not None:
            return automatica
        historicos.append(("agente", list(mensagens)))
        return fila.pop(0)

    return chat, historicos


def test_spec_que_diverge_do_pedido_e_reescrita_com_o_relatorio(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC_TEXTO, SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        {"revisao_spec": [spec_revisada(False, "o pedido não fala em string"), spec_revisada(True)]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert "fatorial(5) == 120" in (tmp_path / ".minicode" / "specification.md").read_text(encoding="utf-8")
    # a 2ª chamada da spec recebeu o relatório da revisão
    chamadas_da_spec = [ms for papel, ms in historicos if papel == "agente" and "ESPECIFICAÇÃO" in ms[0]["content"]]
    ultimo = chamadas_da_spec[-1]
    assert any("o pedido não fala em string" in m["content"] for m in ultimo if m["role"] == "user")


def test_spec_reprovada_sempre_segue_depois_de_duas_correcoes(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, SPEC, SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        {"revisao_spec": [spec_revisada(False)] * 3},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert "spec_reprovada_seguindo" in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_com_a_revisao_desligada_a_spec_nao_e_revisada(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish")],
        {},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, revisar_spec=False)

    assert execucao.estado == DONE
    assert execucao.chamadas_llm == 6   # 5 + plano de testes (sem a revisão dele)


# --- diagnóstico da falha e restrição do reparo ---

def diagnostico(classificacao, evidencias="evidência", proxima="próxima ação", citacao="fatorial(5) == 120"):
    # a citação padrão existe de verdade na SPEC dos testes; passe outra para testar a ancoragem
    return json.dumps({"classificacao": classificacao, "citacao_da_spec": citacao,
                       "evidencias": evidencias, "proxima_acao": proxima})


def eventos_do_tipo(tmp_path, tipo):
    return [e for e in eventos_do_registro(tmp_path) if e["tipo"] == tipo]


def test_falha_de_teste_passa_pelo_estado_diagnosing_antes_de_reparar(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("tests/test_fat_2.py", TESTES),
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG", "o teste espera 121")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    mudancas = [(e["de"], e["para"]) for e in eventos_do_tipo(tmp_path, "mudanca_estado")]
    assert ("VERIFYING", "DIAGNOSING") in mudancas
    assert ("DIAGNOSING", "REPAIRING") in mudancas
    assert eventos_do_tipo(tmp_path, "diagnostico")[0]["classificacao"] == "TEST_BUG"


def test_o_reparo_recebe_o_diagnostico_e_a_restricao(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("tests/test_fat_2.py", TESTES),
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG", "o teste espera 121", "corrigir o valor esperado")]},
    )

    rodar_agente("crie fatorial", tmp_path, chat)

    ultimo = [ms for papel, ms in historicos if papel == "agente"][-1]
    reparo = [m["content"] for m in ultimo if m["role"] == "user" and "REMOVEU" in m["content"]]
    assert reparo
    assert "test_cinco" in reparo[0]
    assert "corrigir o valor esperado" in reparo[0]
    assert "== 121" not in reparo[0]   # o teste errado não aparece mais


def test_test_bug_impede_alterar_o_codigo_no_reparo(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("fat.py", FATORIAL_ERRADO),            # tentativa de mexer no código: recusada
         escrever("tests/test_fat_2.py", TESTES),
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert (tmp_path / "fat.py").read_text(encoding="utf-8") == FATORIAL_CERTO   # o código ficou intacto
    assert "escrita_restrita" in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_code_bug_impede_alterar_os_testes_no_reparo(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),
         escrever("tests/test_fat.py", "def test_enfraquecido():\n    assert True\n"),   # recusada
         escrever("fat.py", FATORIAL_CERTO),
         acao("finish")],
        {"diagnostico": [diagnostico("CODE_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert (tmp_path / "tests" / "test_fat.py").read_text(encoding="utf-8") == TESTES   # o teste ficou intacto
    assert "escrita_restrita" in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_diagnostico_unknown_nao_restringe_nada(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),
         escrever("fat.py", FATORIAL_CERTO),
         acao("finish")],
        {"diagnostico": [diagnostico("UNKNOWN")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert "escrita_restrita" not in [e["tipo"] for e in eventos_do_registro(tmp_path)]


def test_diagnostico_que_nao_resolveu_nao_prende_o_reparo_seguinte(tmp_path):
    # O teste que falha já existia no projeto: o programa corrige o diagnóstico para CODE_BUG (só o código
    # muda). Se o reparo não mudou o resultado (repetiu), a restrição é levantada no reparo seguinte.
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_fat.py").write_text(TESTES, encoding="utf-8")   # teste que já existia: protegido
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         acao("finish"),                                  # falha 1 -> TEST_BUG (restringe a testes)
         acao("finish"),                                  # falha idêntica -> repetiu: sem restrição
         escrever("fat.py", FATORIAL_CERTO),              # agora o código pode mudar
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG"), diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    restricoes = [e["restricao"] for e in eventos_do_tipo(tmp_path, "restricao_do_reparo")]
    assert restricoes == ["codigo", None]


def test_diagnostico_desligado_vai_direto_para_o_reparo(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),
         escrever("fat.py", FATORIAL_CERTO),
         acao("finish")],
        {},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, diagnosticar=False)

    assert execucao.estado == DONE
    assert "DIAGNOSING" not in [e["para"] for e in eventos_do_tipo(tmp_path, "mudanca_estado")]


def test_diagnostico_com_citacao_inventada_e_rebaixado_e_nao_restringe(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         escrever("tests/test_fat.py", TESTES),
         acao("finish"),
         escrever("fat.py", FATORIAL_CERTO),            # só passa se a restrição de testes NÃO existir
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG", citacao="a especificação exige algo que ela nunca disse")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "diagnostico_rebaixado")
    assert eventos_do_tipo(tmp_path, "diagnostico")[0]["classificacao"] == "UNKNOWN"
    assert [e["restricao"] for e in eventos_do_tipo(tmp_path, "restricao_do_reparo")] == [None]


def test_diagnostico_com_citacao_verdadeira_restringe(tmp_path):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("tests/test_fat_2.py", TESTES),         # muda o teste que falhou: aceito
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG", citacao="fatorial(5) == 120")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "testes_removidos")[0]["testes"] == ["test_cinco"]
    assert "test_cinco" not in (tmp_path / "tests" / "test_fat.py").read_text(encoding="utf-8")
    assert not eventos_do_tipo(tmp_path, "diagnostico_rebaixado")


def reparar_com_diagnostico(tmp_path, classificacao):
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),
         escrever("tests/test_fat_2.py", TESTES),
         acao("finish")],
        {"diagnostico": [diagnostico(classificacao)]},
    )
    execucao = rodar_agente("crie fatorial", tmp_path, chat)
    ultimo = [ms for papel, ms in historicos if papel == "agente"][-1]
    return execucao, "\n".join(m["content"] for m in ultimo)


def test_test_bug_remove_o_teste_e_mantem_o_plano_de_testes(tmp_path):
    # o teste é que não seguiu o plano: o plano continua valendo e o modelo o recebe
    execucao, conversa = reparar_com_diagnostico(tmp_path, "TEST_BUG")

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "testes_removidos")
    assert not eventos_do_tipo(tmp_path, "plano_de_testes_corrigido")
    assert "Plano de testes" in conversa


def test_plan_bug_corrige_o_plano_antes_de_reescrever_o_teste(tmp_path):
    # o teste seguiu um plano errado: o plano é corrigido (nova chamada) e só então o teste é refeito
    execucao, conversa = reparar_com_diagnostico(tmp_path, "PLAN_BUG")

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "plano_de_testes_corrigido")
    assert eventos_do_tipo(tmp_path, "testes_removidos")
    assert "Plano de testes" in conversa

    # o diagrama mostra a volta: DIAGNOSING -> TEST_PLANNED -> REPAIRING
    mudancas = [(e["de"], e["para"]) for e in eventos_do_tipo(tmp_path, "mudanca_estado")]
    assert ("DIAGNOSING", "TEST_PLANNED") in mudancas and ("TEST_PLANNED", "REPAIRING") in mudancas

    # e o reparo registra a etapa do erro e a ação
    reparo = eventos_do_tipo(tmp_path, "reparo")[0]
    assert reparo["culpado"] == "PLAN_BUG" and "TEST_PLANNED" in reparo["etapa"] and reparo["acao"]
    assert "test_cinco" not in (tmp_path / "tests" / "test_fat.py").read_text(encoding="utf-8")


def test_plan_bug_restringe_o_reparo_aos_testes(tmp_path):
    from minicode.agent.estados import Execucao
    execucao = Execucao("t")
    execucao.registrar_diagnostico({"classificacao": "PLAN_BUG"})
    assert execucao.restricao_escrita == "testes"


def test_falha_repetida_depois_de_reescrever_o_teste_sobe_para_o_plano(tmp_path):
    # o teste é reescrito mas a falha volta idêntica: a origem está no plano de testes
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_ERRADO),
         acao("finish"),                                  # falha 1 -> TEST_BUG: teste removido e reescrito
         escrever("tests/test_fat_2.py", TESTE_ERRADO),   # reescrito igual: a falha volta idêntica
         acao("finish"),                                  # falha 2 -> escalada para PLAN_BUG
         escrever("tests/test_fat_3.py", TESTES),
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG"), diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "reparo_escalado")
    assert eventos_do_tipo(tmp_path, "plano_de_testes_corrigido")


TESTE_MISTO = (
    "from fat import fatorial\n\n"
    "def test_zero():\n    assert fatorial(0) == 1\n\n"
    "def test_cinco():\n    assert fatorial(5) == 121\n"
)
TESTE_TEIMOSO = "from fat import fatorial\n\ndef test_cinco_de_novo():\n    assert fatorial(5) == 121\n"


def test_no_fim_o_programa_descarta_o_teste_do_modelo_que_continua_falhando(tmp_path):
    # o código está certo; o teste escrito pelo modelo está errado e ele o reescreve errado de novo.
    # Sem tentativas sobrando e com o diagnóstico apontando o teste, o teste não confiável é descartado.
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_CERTO),
         escrever("tests/test_fat.py", TESTE_MISTO),
         acao("finish"),                                   # falha 1 -> TEST_BUG: remove test_cinco
         escrever("tests/test_fat_2.py", TESTE_TEIMOSO),   # o modelo repete o mesmo erro
         acao("finish")],                                  # falha 2: acabaram as tentativas
        {"diagnostico": [diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_tentativas=1)

    assert execucao.estado == DONE
    assert execucao.testes_passaram is True
    assert execucao.testes_descartados == ["test_cinco_de_novo"]
    assert eventos_do_tipo(tmp_path, "testes_descartados")
    assert "test_zero" in (tmp_path / "tests" / "test_fat.py").read_text(encoding="utf-8")   # o teste bom ficou


def test_o_programa_nao_descarta_teste_que_ja_existia(tmp_path):
    # o teste que falha é do projeto (confiável): o código é que está errado, e o agente falha
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_fat.py").write_text(TESTES, encoding="utf-8")
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         acao("finish"),
         escrever("fat.py", FATORIAL_ERRADO),
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat, max_tentativas=1)

    assert execucao.estado == FAILED
    assert execucao.testes_descartados == []


def test_teste_que_ja_existia_nunca_e_o_culpado(tmp_path):
    # o diagnóstico da LLM culpa o teste do projeto, mas ele é o oráculo confiável: o programa o corrige
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_fat.py").write_text(TESTES, encoding="utf-8")
    chat, historicos = chat_scriptado(
        [SPEC, PLANO,
         escrever("fat.py", FATORIAL_ERRADO),
         acao("finish"),                        # o teste do projeto falha
         escrever("fat.py", FATORIAL_CERTO),    # só o código pode mudar
         acao("finish")],
        {"diagnostico": [diagnostico("TEST_BUG")]},
    )

    execucao = rodar_agente("crie fatorial", tmp_path, chat)

    assert execucao.estado == DONE
    assert eventos_do_tipo(tmp_path, "diagnostico_corrigido_pelo_programa")
    assert eventos_do_tipo(tmp_path, "reparo")[0]["culpado"] == "CODE_BUG"
    ultimo = [ms for papel, ms in historicos if papel == "agente"][-1]
    assert any("já existia no projeto" in m["content"] for m in ultimo)


def test_arquivos_dos_testes_que_falharam_le_o_resumo_do_pytest():
    from minicode.tools.testes import arquivos_dos_testes_que_falharam
    saida = "FAILED tests/test_original.py::test_criar - AttributeError\nFAILED tests\\test_b.py::test_x - assert"
    assert arquivos_dos_testes_que_falharam(saida) == ["tests/test_original.py", "tests/test_b.py"]

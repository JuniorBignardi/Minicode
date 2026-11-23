"""Auditoria por função: quanto cada chamada à LLM do agente erra, medido com a solução de referência.

Uso:  python experiments/diagnostico_parte1/auditoria_funcoes.py <pasta_dos_resultados>
Lê as execuções gravadas por rodar_instrumentado.py (chamadas_llm.jsonl, actions.jsonl, resultado.json).

Funções medidas:
  spec               a spec tem um valor errado em algum critério (e o plano de testes o repete)?
  plano de testes    quantos casos têm valor esperado errado?
  ação (ferramenta)  quantas ações do modelo dão erro ou são recusadas?
  código             a primeira versão que o agente escreve está certa? o reparo conserta o que está errado?
  revisor do código  aprova código certo e reprova código errado?
  diagnóstico        o veredito concorda com o oráculo?
"""
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))   # experiments/ (oraculo)
sys.path.insert(0, str(AQUI.parents[1] / "src"))

import oraculo
from minicode.llm.parser import extrair_acoes

# tipos de evento do rastro do agente que indicam uma ação recusada ou mal formada
ERROS_DE_ACAO = (
    "ferramenta_proibida", "acao_repetida", "formato_invalido", "limite_de_leituras", "finish_recusado",
    "escrita_protegida", "escrita_restrita", "escrita_sem_leitura", "escrita_invalida", "escrita_perde_testes",
    "escrita_sem_mudanca",
)


def execucoes(base):
    # uma tupla por execução gravada: (pasta, conjunto, resultado.json, chamadas à LLM, eventos do agente)
    for resultado in sorted(base.glob("*_r*/tarefa_*/resultado.json")):
        pasta = resultado.parent
        r = json.loads(resultado.read_text(encoding="utf-8"))
        conjunto = "facil" if pasta.parent.name.startswith("facil") else "dificil"
        chamadas = [
            json.loads(l)
            for l in (pasta / ".minicode" / "chamadas_llm.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        eventos = [
            json.loads(l)
            for l in (pasta / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        yield pasta, conjunto, r, chamadas, eventos


def final_certo(r):
    # a execução acabou bem: o agente declarou DONE e o verificador oculto aprovou o código
    return r["estado"] == "DONE" and r["codigo_correto"]


def porcentagem(parte, total):
    return f"{100 * parte / total:.0f}%" if total else "-"


def verificar(conjunto, id, arquivos):
    # roda o verificador oculto sobre os arquivos (dict caminho -> texto) somados aos iniciais da tarefa
    tarefa = oraculo.tarefa_e_referencia(conjunto, id)[0]
    pasta = Path(tempfile.mkdtemp())
    try:
        oraculo.escrever(pasta, {**tarefa["arquivos"], **arquivos})
        return bool(tarefa["verificar"](pasta))
    except Exception:
        return False
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


# --- ação: seleção de ferramenta e argumentos ---

def auditar_acoes(todas):
    total = erradas = 0
    # rodadas_com_erro[grupo] = [execuções com algum erro de ação, execuções do grupo]
    por_tipo, rodadas_com_erro = Counter(), {"errou": [0, 0], "acertou": [0, 0]}
    limite = 0
    for pasta, conjunto, r, chamadas, eventos in todas:
        ferramentas = [e for e in eventos if e["tipo"] == "ferramenta"]
        total += len(ferramentas)
        erradas += sum(not e["ok"] for e in ferramentas)
        problemas = [e["tipo"] for e in eventos if e["tipo"] in ERROS_DE_ACAO]
        por_tipo.update(problemas)
        grupo = "acertou" if final_certo(r) else "errou"
        rodadas_com_erro[grupo][0] += bool(problemas or any(not e["ok"] for e in ferramentas))
        rodadas_com_erro[grupo][1] += 1
        limite += r["iteracoes"] >= 40   # 40 é o limite de iterações do agente
    return {
        "acoes": total, "com_erro": erradas, "problemas": dict(por_tipo.most_common()),
        "execucoes_no_limite_de_iteracoes": limite,
        "execucoes_com_algum_problema": rodadas_com_erro,
    }


# --- código: a primeira versão e o reparo ---

def primeira_versao(chamadas, inicial):
    # os arquivos que o agente tinha gravado até o primeiro finish (reproduz as ações, sem refazer os gates)
    arquivos = dict(inicial)
    for chamada in chamadas:
        if chamada["fase"] != "acao" or not chamada["resposta"]:
            continue
        for acao in extrair_acoes(chamada["resposta"]):
            if acao.get("tool") == "finish":
                return arquivos
            if acao.get("tool") in ("create_file", "write_file") and isinstance(acao.get("args"), dict):
                caminho, conteudo = acao["args"].get("path"), acao["args"].get("content")
                if isinstance(caminho, str) and isinstance(conteudo, str):
                    # conteúdo com "\n" literal e sem quebras de linha de verdade: desfaz o escape
                    if "\\n" in conteudo and "\n" not in conteudo:
                        conteudo = conteudo.replace("\\n", "\n")
                    arquivos[caminho] = conteudo
    return arquivos


def auditar_codigo(todas):
    # conta "primeira versão -> versão final", cada uma certa ou errada, pelo verificador oculto
    contagem = Counter()
    for pasta, conjunto, r, chamadas, eventos in todas:
        if r["tipo"] == "criar testes":
            continue
        tarefa = oraculo.tarefa_e_referencia(conjunto, r["id"])[0]
        inicio = verificar(conjunto, r["id"], primeira_versao(chamadas, tarefa["arquivos"]))
        fim = r["codigo_correto"]
        contagem[("certo" if inicio else "errado") + "->" + ("certo" if fim else "errado")] += 1
    return contagem


# --- revisor do código ---

def arquivos_do_prompt(texto):
    # lê os arquivos que o prompt do revisor mostra, cada um introduzido por uma linha "--- caminho"
    arquivos = {}
    for bloco in texto.split("\n--- ")[1:] if "\n--- " in texto else []:
        caminho, _, conteudo = bloco.partition("\n")
        arquivos[caminho.strip()] = conteudo.split("\n\nSaída")[0].rstrip() + "\n"
    return arquivos


def auditar_revisor(todas):
    # matriz[(estado do código, veredito do revisor)] = quantidade
    matriz = Counter()
    for pasta, conjunto, r, chamadas, eventos in todas:
        if r["tipo"] == "criar testes":
            continue
        for chamada in chamadas:
            # só as revisões do código contra a spec (o prompt de sistema cita "sobre_o_codigo")
            if (
                chamada["fase"] != "revisao"
                or "sobre_o_codigo" not in chamada["mensagens"][0]["content"]
                or not chamada["resposta"]
            ):
                continue
            try:
                criterios = json.loads(chamada["resposta"])["criterios"]
            except (json.JSONDecodeError, KeyError):
                continue
            aprovou = all(c.get("atendido") for c in criterios if c.get("sobre_o_codigo", True))
            arquivos = arquivos_do_prompt(chamada["mensagens"][1]["content"].split("Arquivos")[-1])
            matriz[(
                "codigo certo" if verificar(conjunto, r["id"], arquivos) else "codigo errado",
                "aprovou" if aprovou else "reprovou",
            )] += 1
    return matriz


# --- spec: valor errado nos critérios ---

def auditar_spec(todas):
    # estimativa mínima: só conta o valor errado da spec que o plano de testes repete
    tinham_exemplos = com_valor_errado = 0
    for pasta, conjunto, r, chamadas, eventos in todas:
        spec = (pasta / ".minicode" / "specification.md").read_text(encoding="utf-8")
        casos = r["plano_de_testes"] or []
        if not casos:
            continue
        referencia = oraculo.montar_projeto(conjunto, r["id"], Path(tempfile.mkdtemp()))
        try:
            saidas = oraculo.executar_entradas(referencia, [c["entrada"] for c in casos])
        finally:
            shutil.rmtree(referencia, ignore_errors=True)
        tinham_exemplos += 1
        # um caso com valor errado cujo valor errado também está escrito na spec, ao lado da entrada
        com_valor_errado += any(
            oraculo.comparar(s, c["esperado"]) == "errado"
            and c["esperado"].strip() in spec
            and c["entrada"].split("(")[0] in spec
            for c, s in zip(casos, saidas)
        )
    return tinham_exemplos, com_valor_errado


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = Path(sys.argv[1])
    todas = list(execucoes(base))
    print(f"# Auditoria por função: {len(todas)} execuções do agente com o Qwen 14B\n")

    # --- ação: a ferramenta e os argumentos que o modelo escolheu ---
    a = auditar_acoes(todas)
    print("## Ação (escolha da ferramenta e dos argumentos)")
    print(f"- {a['acoes']} chamadas de ferramenta; {a['com_erro']} deram erro ({porcentagem(a['com_erro'], a['acoes'])})")
    print(f"- problemas contados: {a['problemas']}")
    print(f"- execuções que bateram o limite de 40 iterações: {a['execucoes_no_limite_de_iteracoes']}")
    for grupo, (n, t) in a["execucoes_com_algum_problema"].items():
        print(f"- entre as que {grupo}: {n}/{t} ({porcentagem(n, t)}) tiveram algum erro de ação")

    # --- código: a primeira versão estava certa? o reparo consertou? o processo estragou código certo? ---
    c = auditar_codigo(todas)
    total = sum(c.values())
    print("\n## Código (primeira versão e reparo), sem as tarefas de criar testes")
    for chave, n in c.most_common():
        print(f"- primeira versão e final: {chave}: {n}")
    certas = c["certo->certo"] + c["certo->errado"]
    print(f"- a primeira versão do código estava certa em {certas}/{total} ({porcentagem(certas, total)})")
    erradas = c["errado->certo"] + c["errado->errado"]
    print(
        f"- das que nasceram erradas, o reparo consertou {c['errado->certo']}/{erradas} "
        f"({porcentagem(c['errado->certo'], erradas)})"
    )
    print(f"- código certo estragado pelo processo: {c['certo->errado']}")

    # --- revisor do código: aprova o que está certo e reprova o que está errado? ---
    m = auditar_revisor(todas)
    print("\n## Revisor do código (compara o código com a spec)")
    for (codigo, veredito), n in sorted(m.items()):
        print(f"- {codigo} e o revisor {veredito}: {n}")
    certo_total = m[("codigo certo", "aprovou")] + m[("codigo certo", "reprovou")]
    errado_total = m[("codigo errado", "aprovou")] + m[("codigo errado", "reprovou")]
    print(
        f"- reprova código que estava certo: {m[('codigo certo', 'reprovou')]}/{certo_total} "
        f"({porcentagem(m[('codigo certo', 'reprovou')], certo_total)})"
    )
    print(
        f"- aprova código que estava errado: {m[('codigo errado', 'aprovou')]}/{errado_total} "
        f"({porcentagem(m[('codigo errado', 'aprovou')], errado_total)})"
    )

    # --- spec: valor errado nos critérios ---
    n, errada = auditar_spec(todas)
    print("\n## Spec")
    print(
        f"- {errada} de {n} execuções ({porcentagem(errada, n)}) têm um valor errado escrito na spec "
        f"que o plano de testes repete (estimativa mínima)"
    )


if __name__ == "__main__":
    main()

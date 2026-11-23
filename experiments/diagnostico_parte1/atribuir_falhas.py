"""Atribui cada erro do agente à etapa que o causou, usando as soluções de referência como oráculo.

Uso:  python experiments/diagnostico_parte1/atribuir_falhas.py <pasta_dos_resultados>
Lê as execuções gravadas por rodar_instrumentado.py e gera, na mesma pasta,
diagnostico_falhas.md (o relatório) e diagnostico_falhas.json (uma linha por execução).

Para cada execução mede:
  plano de testes   quantos casos têm valor esperado errado (executando a entrada na referência)
  testes do agente  se algum teste que o agente escreveu falha contra a referência (teste errado)
  diagnóstico       se o veredito do modelo concorda com o oráculo (código ou teste errado?)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py

import oraculo


def eventos(pasta, tipo):
    arquivo = pasta / ".minicode" / "actions.jsonl"
    if not arquivo.is_file():
        return []
    todos = [json.loads(linha) for linha in arquivo.read_text(encoding="utf-8").splitlines() if linha.strip()]
    return [e for e in todos if e.get("tipo") == tipo]


def lado_do_veredito(classificacao):
    # PLAN_BUG é erro do teste (que seguiu um plano ruim); UNKNOWN e ENVIRONMENT_ERROR não apontam ninguém
    return {"CODE_BUG": "CODE_BUG", "TEST_BUG": "TEST_BUG", "PLAN_BUG": "TEST_BUG"}.get(classificacao, "indeterminado")


def categoria(r):
    # como a execução terminou, combinando o estado do agente com o código final estar certo ou errado
    if r["estado"] == "DONE" and r["codigo_correto"]:
        return "correto"
    if r["estado"] == "DONE":
        return "DONE com código errado"
    return "FAILED com código certo" if r["codigo_correto"] else "FAILED com código errado"


def analisar_execucao(pasta, conjunto):
    r = json.loads((pasta / "resultado.json").read_text(encoding="utf-8"))

    # 1) plano de testes: cada caso é executado na referência (correto, errado ou inavaliável)
    avaliacoes = oraculo.avaliar_casos(conjunto, r["id"], r["plano_de_testes"]) if r["plano_de_testes"] else []

    # 2) testes que o agente escreveu e que falham contra a referência
    arquivos_de_teste = [a for a in r["arquivos_alterados"] if oraculo.e_teste(a)]
    testes_errados = oraculo.testes_errados_do_agente(conjunto, r["id"], pasta, arquivos_de_teste)

    # 3) diagnósticos: o veredito do modelo contra o do oráculo, no projeto como estava naquele momento
    diagnosticos = []
    snapshots = (
        sorted((pasta / ".minicode" / "snapshots").glob("diag_*"))
        if (pasta / ".minicode" / "snapshots").is_dir()
        else []
    )
    for snapshot, evento in zip(snapshots, eventos(pasta, "diagnostico")):
        diagnosticos.append({
            "modelo": lado_do_veredito(evento["classificacao"]),
            "classificacao": evento["classificacao"],
            "oraculo": oraculo.veredito_do_oraculo(conjunto, r["id"], snapshot),
        })

    return {
        **{k: r[k] for k in ("id", "nome", "tipo", "estado", "codigo_correto", "reparos", "chamadas", "segundos")},
        "conjunto": conjunto, "rodada": pasta.parent.name, "categoria": categoria(r),
        "casos": Counter(avaliacoes), "testes_errados": sorted(testes_errados), "diagnosticos": diagnosticos,
        "plano_errado": "errado" in avaliacoes, "testes_do_agente_errados": bool(testes_errados),
        # só conta como diagnóstico errado quando os dois lados apontam alguém e discordam
        "diagnostico_errado": any(
            d["oraculo"] in ("CODE_BUG", "TEST_BUG") and d["modelo"] in ("CODE_BUG", "TEST_BUG")
            and d["modelo"] != d["oraculo"]
            for d in diagnosticos
        ),
    }


def porcentagem(parte, total):
    return f"{100 * parte / total:.0f}%" if total else "-"


def relatorio(linhas):
    erros = [x for x in linhas if x["categoria"] != "correto"]
    certas = [x for x in linhas if x["categoria"] == "correto"]

    # --- seção 1: como as execuções terminaram ---
    saida = [
        f"# Diagnóstico de falhas do agente (Qwen 14B)", "",
        f"{len(linhas)} execuções; {len(erros)} com resultado errado ({porcentagem(len(erros), len(linhas))}).", "",
        "## 1. Como as execuções terminaram", "", "| Categoria | Execuções |", "|---|---|",
    ]
    for nome, n in Counter(x["categoria"] for x in linhas).most_common():
        saida.append(f"| {nome} | {n} |")

    # --- seção 2: o que o oráculo encontrou nas execuções que erraram (e nas que acertaram, como controle) ---
    saida += [
        "", "## 2. O que há de errado nas execuções que erraram (e, de controle, nas que acertaram)", "",
        "| Sinal medido pelo oráculo | Nas que erraram | Nas que acertaram |", "|---|---|---|",
    ]
    for rotulo, chave in (
        ("plano de testes com valor esperado errado", "plano_errado"),
        ("teste escrito pelo agente que falha na referência", "testes_do_agente_errados"),
        ("diagnóstico que contradiz o oráculo", "diagnostico_errado"),
    ):
        saida.append(
            f"| {rotulo} | {sum(x[chave] for x in erros)}/{len(erros)} "
            f"({porcentagem(sum(x[chave] for x in erros), len(erros))})"
            f" | {sum(x[chave] for x in certas)}/{len(certas)} "
            f"({porcentagem(sum(x[chave] for x in certas), len(certas))}) |"
        )
    sem_sinal = [x for x in erros if not (x["plano_errado"] or x["testes_do_agente_errados"] or x["diagnostico_errado"])]
    saida.append(
        f"| nenhum dos três (spec, código ou outra causa) | {len(sem_sinal)}/{len(erros)} "
        f"({porcentagem(len(sem_sinal), len(erros))}) | - |"
    )

    # --- seção 3: valores esperados do plano de testes ---
    casos = Counter()
    for x in linhas:
        casos.update(x["casos"])
    avaliaveis = casos["correto"] + casos["errado"]
    saida += [
        "", "## 3. Valores esperados do plano de testes", "",
        f"{avaliaveis} casos avaliáveis (mais {casos['inavaliavel']} que a referência não consegue executar): "
        f"{casos['errado']} com valor esperado errado ({porcentagem(casos['errado'], avaliaveis)}).", "",
        "| Tarefa | Casos errados | Casos avaliáveis |", "|---|---|---|",
    ]
    por_tarefa = defaultdict(Counter)
    for x in linhas:
        por_tarefa[(x["conjunto"], x["id"], x["nome"])].update(x["casos"])
    # as 10 tarefas com maior fração de casos errados
    ordem = sorted(por_tarefa.items(), key=lambda kv: -kv[1]["errado"] / max(kv[1]["correto"] + kv[1]["errado"], 1))
    for (conjunto, id, nome), c in ordem[:10]:
        saida.append(f"| {conjunto} {id:02d} {nome} | {c['errado']} | {c['correto'] + c['errado']} |")

    # --- seção 4: diagnósticos do modelo contra o oráculo ---
    todos = [d for x in linhas for d in x["diagnosticos"]]
    comparaveis = [
        d for d in todos
        if d["oraculo"] in ("CODE_BUG", "TEST_BUG") and d["modelo"] in ("CODE_BUG", "TEST_BUG")
    ]
    certos = sum(d["modelo"] == d["oraculo"] for d in comparaveis)
    saida += [
        "", "## 4. Diagnósticos", "",
        f"{len(todos)} diagnósticos; {len(comparaveis)} comparáveis com o oráculo; "
        f"o modelo acertou {certos} ({porcentagem(certos, len(comparaveis))}).", "",
        "| Oráculo | Modelo disse CODE_BUG | Modelo disse TEST_BUG ou PLAN_BUG | Indeterminado |", "|---|---|---|---|",
    ]
    for lado in ("CODE_BUG", "TEST_BUG", "MISTO", "sem_falha", "nao_aplicavel"):
        c = Counter(d["modelo"] for d in todos if d["oraculo"] == lado)
        saida.append(f"| {lado} | {c['CODE_BUG']} | {c['TEST_BUG']} | {c['indeterminado']} |")

    # --- seção 5: a etapa líder, pela regra definida antes de rodar ---
    fracoes = {
        "plano de testes com valor esperado errado": sum(x["plano_errado"] for x in erros),
        "testes escritos pelo agente errados": sum(x["testes_do_agente_errados"] for x in erros),
        "diagnóstico errado": sum(x["diagnostico_errado"] for x in erros),
    }
    lider = max(fracoes, key=fracoes.get)
    saida += [
        "", "## 5. Regra de decisão (definida antes de rodar)", "",
        "A função a especializar é a etapa com maior fração dos resultados errados, "
        "desde que tenha métrica automática.", "",
        f"Etapa líder: **{lider}** ({fracoes[lider]} de {len(erros)} execuções com resultado errado).", "",
    ]
    return "\n".join(saida)


def main():
    pasta = Path(sys.argv[1])
    linhas = []

    # uma linha por execução (as pastas são facil_rN/tarefa_NN ou dificil_rN/tarefa_NN)
    for resultado in sorted(pasta.glob("*_r*/tarefa_*/resultado.json")):
        conjunto = "facil" if resultado.parent.parent.name.startswith("facil") else "dificil"
        linhas.append(analisar_execucao(resultado.parent, conjunto))
        print(f"{resultado.parent.parent.name}/{resultado.parent.name}: {linhas[-1]['categoria']}", flush=True)

    (pasta / "diagnostico_falhas.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")
    (pasta / "diagnostico_falhas.md").write_text(relatorio(linhas), encoding="utf-8")
    print("\nrelatório em", pasta / "diagnostico_falhas.md")


if __name__ == "__main__":
    main()

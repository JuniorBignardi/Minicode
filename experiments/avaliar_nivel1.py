"""Nível 1: o plano de testes que um modelo escreve, conferido pelo oráculo (a solução de referência de cada tarefa).

Uso:
  python experiments/avaliar_nivel1.py baseline <pasta_dos_resultados_do_14b> [saida.json]
      o Qwen 14B da Parte 1, pelas respostas gravadas nos logs das 60 execuções
  python experiments/avaliar_nivel1.py endpoint <pasta_dos_resultados_do_14b> <url_base> <modelo> [saida.json]
      um modelo servido por uma API compatível com a da OpenAI (chave em MINICODE_API_KEY, se precisar)

As entradas do teste são os prompts REAIS que o agente mandou ao 14B na etapa do plano de testes
(pedido, spec e plano das 25 tarefas). Para cada prompt (sem repetir), vale a primeira resposta.
Cada caso do plano é executado na referência: correto, errado ou inavaliável.
Métrica principal: corretos / (corretos + errados). O intervalo de 95% é bootstrap sobre as tarefas.
"""
import json
import os
import random
import re
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "src"))

import oraculo
from minicode.spec.plano_de_testes import criterios_da_spec, interpretar_plano_de_testes, validar_plano_de_testes


PROMPTS_VERSIONADOS = AQUI.parent / "datasets" / "plano_de_testes" / "entradas_reais.json"


# ---------- as entradas: os prompts reais da Parte 1 ----------

def entradas_reais(base):
    # os prompts do plano de testes das 60 execuções, sem repetir, com a resposta que o 14B deu.
    # Sem os logs da Parte 1 (pasta ignorada pelo git), usa os mesmos 60 prompts versionados no repositório
    # (sem a resposta do 14B).
    base = Path(base)
    if not (base / "diagnostico_falhas.json").is_file():
        return json.loads(PROMPTS_VERSIONADOS.read_text(encoding="utf-8"))

    execucoes = json.loads((base / "diagnostico_falhas.json").read_text(encoding="utf-8"))
    vistos, entradas = set(), []
    for e in execucoes:
        arquivo = base / e["rodada"] / f"tarefa_{e['id']:02d}" / ".minicode" / "chamadas_llm.jsonl"
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if not linha.strip():
                continue
            chamada = json.loads(linha)
            if chamada["fase"] != "plano_de_testes":
                continue
            # o mesmo prompt pode aparecer em várias chamadas: guarda só a primeira
            chave = (e["conjunto"], e["id"], chamada["mensagens"][1]["content"])
            if chave not in vistos:
                vistos.add(chave)
                entradas.append({
                    "conjunto": e["conjunto"],
                    "id": e["id"],
                    "mensagens": chamada["mensagens"][:2],
                    "resposta_14b": chamada["resposta"],
                })
    return entradas


def spec_da_mensagem(usuario):
    # a especificação está entre "Especificação:" e "Plano:" na mensagem do usuário
    achou = re.search(r"Especificação:\n(.*?)\n\nPlano:\n", usuario, re.S)
    return achou.group(1) if achou else ""


# ---------- ler a resposta do modelo e pontuar ----------

def interpretar(resposta):
    # tolerante com texto em volta do JSON (cerca de código, frase antes), igual para todos os modelos
    inicio, fim = resposta.find("{"), resposta.rfind("}")
    return interpretar_plano_de_testes(resposta[inicio:fim + 1]) if 0 <= inicio < fim else None


def pontuar(entradas, gerar=None):
    # gerar(mensagens) -> texto; sem gerar, usa a resposta que o 14B deu nos logs
    resultados = []
    for e in entradas:
        resposta = gerar(e["mensagens"]) if gerar else e["resposta_14b"]
        casos = interpretar(resposta or "")
        criterios = criterios_da_spec(spec_da_mensagem(e["mensagens"][1]["content"]))
        valido = casos is not None and validar_plano_de_testes(criterios, casos)[0]
        notas = oraculo.avaliar_casos(e["conjunto"], e["id"], casos) if casos else []
        resultados.append({
            "tarefa": f"{e['conjunto']}_{e['id']}",
            "formato_ok": casos is not None,
            "plano_valido": valido,
            "notas": notas,
        })
    return resultados


# ---------- a métrica: corretos / (corretos + errados), com intervalo por bootstrap ----------

def fracao_correta(notas):
    # os "inavaliavel" ficam fora da conta
    corretos, errados = notas.count("correto"), notas.count("errado")
    return corretos / (corretos + errados) if corretos + errados else None


def resumo(resultados, repeticoes=1000, semente=0):
    notas = [n for r in resultados for n in r["notas"]]

    # junta as notas de cada tarefa: o bootstrap sorteia TAREFAS, não casos soltos
    por_tarefa = {}
    for r in resultados:
        por_tarefa.setdefault(r["tarefa"], []).extend(r["notas"])
    tarefas = list(por_tarefa.values())

    # bootstrap: sorteia tarefas com reposição e recalcula a fração correta, 1000 vezes
    rng, sorteios = random.Random(semente), []
    for _ in range(repeticoes):
        amostra = [n for t in (rng.choice(tarefas) for _ in tarefas) for n in t]
        f = fracao_correta(amostra)
        if f is not None:
            sorteios.append(f)
    sorteios.sort()
    # intervalo de 95%: do percentil 2,5 ao 97,5 dos sorteios
    ic = (sorteios[int(0.025 * len(sorteios))], sorteios[int(0.975 * len(sorteios)) - 1]) if sorteios else (None, None)

    return {
        "prompts": len(resultados),
        "tarefas": len(tarefas),
        "formato_ok": sum(r["formato_ok"] for r in resultados) / len(resultados),
        "planos_validos": sum(r["plano_valido"] for r in resultados) / len(resultados),
        "casos_corretos": notas.count("correto"),
        "casos_errados": notas.count("errado"),
        "casos_inavaliaveis": notas.count("inavaliavel"),
        "fracao_correta": fracao_correta(notas),
        "ic95": ic,
    }


def mostrar(nome, r):
    f = r["fracao_correta"]
    texto = (
        "sem casos avaliáveis" if f is None
        else f"{100 * f:.1f}% (IC 95%: {100 * r['ic95'][0]:.1f} a {100 * r['ic95'][1]:.1f})"
    )
    print(
        f"{nome}: {r['prompts']} prompts em {r['tarefas']} tarefas | formato ok {100 * r['formato_ok']:.0f}% | "
        f"planos válidos {100 * r['planos_validos']:.0f}% | "
        f"casos: {r['casos_corretos']} corretos, {r['casos_errados']} errados, {r['casos_inavaliaveis']} inavaliáveis | "
        f"valores corretos: {texto}"
    )


# ---------- chamar um modelo servido por API (compatível com a da OpenAI) ----------

def chamar_endpoint(url_base, modelo, tempo=180):
    chave = os.environ.get("MINICODE_API_KEY", "sem-chave")

    def gerar(mensagens):
        corpo = {"model": modelo, "messages": mensagens, "temperature": 0, "max_tokens": 1500}
        req = urllib.request.Request(
            url_base.rstrip("/") + "/chat/completions",
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=tempo) as r:
            return json.loads(r.read().decode("utf-8"))["choices"][0]["message"].get("content") or ""
    return gerar


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    modo, base = sys.argv[1], sys.argv[2]
    entradas = entradas_reais(base)
    if modo == "baseline":
        gerar, saida = None, sys.argv[3] if len(sys.argv) > 3 else None
    else:
        gerar, saida = chamar_endpoint(sys.argv[3], sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else None
    r = resumo(pontuar(entradas, gerar))
    mostrar("14B (logs da Parte 1)" if modo == "baseline" else sys.argv[4], r)
    if saida:
        Path(saida).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

"""Nível 2: o agente completo nas 25 tarefas, em três configurações (A, B e C), com repetições.

  A  agente como na Parte 1: o Qwen-14B faz tudo (inclusive o plano de testes)
  B  o plano de testes é escrito pelo modelo pequeno ajustado (1,5B + LoRA);
     o 14B faz o resto (revisa o plano, escreve o código, repara)
  C  ablação: o agente sem a etapa do plano de testes (MINICODE_ABLACAO="planejar_testes=False")

Cada (configuração, repetição, conjunto) roda um executor da Parte 1 (eval_tasks/rodar_facil.py ou rodar_dificil.py)
como subprocesso, então a medição é a mesma da Parte 1: o verificador oculto de cada tarefa decide se está correta.

Uso:
  python experiments/nivel2.py rodar  <pasta_de_saida> --repeticoes 3 [--configs A B C] [--conjuntos facil dificil] [--tarefas 1 2 3] [--paralelo 3]
  python experiments/nivel2.py resumo <pasta_de_saida>

Variáveis de ambiente (nenhuma chave é impressa):
  MINICODE_API_BASE, MINICODE_API_KEY, MINICODE_MODEL     o 14B (como na Parte 1)
  MINICODE_PLAN_API_BASE, MINICODE_PLAN_MODEL             o especialista da configuração B (MINICODE_PLAN_API_KEY é opcional)

Retomável: uma execução que já tem resultados.json é pulada. Execuções com erro de infraestrutura
(evento erro_llm: timeout, rede) são contadas à parte no resumo, para não serem confundidas com erro do agente.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXECUTORES = {"facil": RAIZ / "eval_tasks" / "rodar_facil.py", "dificil": RAIZ / "eval_tasks" / "rodar_dificil.py"}
NOMES = {"A": "A: 14B sozinho", "B": "B: 14B + 1,5B ajustado no plano de testes", "C": "C: sem plano de testes (ablação)"}


# ---------------------------------------------------------------------------------------------
# Rodar: um subprocesso do executor da Parte 1 para cada (configuração, repetição, conjunto)
# ---------------------------------------------------------------------------------------------

def ambiente_da_configuracao(config):
    # o que muda entre A, B e C são só variáveis de ambiente: o executor da Parte 1 é o mesmo
    env = dict(os.environ)
    env["MINICODE_PAUSA"] = "0"                      # servidor próprio: sem pausa entre chamadas
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("MINICODE_ABLACAO", None)
    if config == "B":
        assert env.get("MINICODE_PLAN_API_BASE") and env.get("MINICODE_PLAN_MODEL"), "a configuração B precisa de MINICODE_PLAN_API_BASE e MINICODE_PLAN_MODEL"
    else:
        env.pop("MINICODE_PLAN_API_BASE", None)
        env.pop("MINICODE_PLAN_MODEL", None)
    if config == "C":
        env["MINICODE_ABLACAO"] = "planejar_testes=False"
    return env


def eventos_da_tarefa(pasta_tarefa):
    # os eventos que o agente grava (um JSON por linha) em .minicode/actions.jsonl
    arquivo = pasta_tarefa / ".minicode" / "actions.jsonl"
    if not arquivo.is_file():
        return []
    return [json.loads(l) for l in arquivo.read_text(encoding="utf-8").splitlines() if l.strip()]


def rodar_uma(job, saida, tarefas):
    config, rep, conjunto = job
    pasta = saida / f"{config}_r{rep}_{conjunto}"
    # retomável: quem já terminou (tem resultados.json) não roda de novo
    if (pasta / "resultados.json").is_file():
        return job, "pulada (já existe)", 0
    pasta.mkdir(parents=True, exist_ok=True)
    comando = [sys.executable, str(EXECUTORES[conjunto]), str(pasta)] + [str(t) for t in tarefas]
    inicio = time.time()
    with open(pasta / "executor.log", "w", encoding="utf-8") as log:
        r = subprocess.run(
            comando,
            env=ambiente_da_configuracao(config),
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=str(RAIZ / "eval_tasks"),
        )
    return job, f"código {r.returncode}", time.time() - inicio


def rodar(args):
    # caminho ABSOLUTO: os executores rodam dentro de eval_tasks/
    saida = Path(args.saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    # intercalado: A, B, C, A, B, C...
    jobs = [(c, r, s) for r in range(1, args.repeticoes + 1) for s in args.conjuntos for c in args.configs]
    print(f"{len(jobs)} execuções | {args.paralelo} em paralelo | configurações {args.configs} | conjuntos {args.conjuntos}", flush=True)
    inicio = time.time()
    with ThreadPoolExecutor(args.paralelo) as pool:
        for job, estado, segundos in pool.map(lambda j: rodar_uma(j, saida, args.tarefas), jobs):
            print(f"  {job[0]} rep {job[1]} {job[2]:8} {estado} {segundos / 60:.1f} min | total {(time.time() - inicio) / 60:.1f} min", flush=True)
    resumo(args)


# ---------------------------------------------------------------------------------------------
# Resumo: lê os resultados.json, calcula as métricas e a diferença pareada com bootstrap
# ---------------------------------------------------------------------------------------------

def carregar(saida):
    # {config: [ {conjunto, rep, id, correto, ..., erro_llm, especialista} ]}
    por_config = {}
    for pasta in sorted(Path(saida).glob("*_r*_*")):
        if not (pasta / "resultados.json").is_file():
            continue
        config, rep, conjunto = pasta.name.split("_")
        for r in json.loads((pasta / "resultados.json").read_text(encoding="utf-8")):
            eventos = eventos_da_tarefa(pasta / f"tarefa_{r['id']:02d}")
            r = {
                **r,
                "conjunto": conjunto,
                "rep": int(rep[1:]),
                "erro_llm": sum(e["tipo"] == "erro_llm" for e in eventos),
                "usou_especialista": any(e["tipo"] == "plano_de_testes_especialista" for e in eventos),
                "tinha_plano": any(e["tipo"] == "mudanca_estado" and e.get("para") == "TEST_PLANNED" for e in eventos),
            }
            por_config.setdefault(config, []).append(r)
    return por_config


def media(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def por_tarefa(execs):
    # fração de repetições corretas de cada tarefa (o bootstrap reamostra tarefas, não execuções)
    d = {}
    for r in execs:
        d.setdefault((r["conjunto"], r["id"]), []).append(bool(r["correto"]))
    return {k: media(v) for k, v in d.items()}


def bootstrap(vetores, estatistica, repeticoes=2000, semente=0):
    # vetores: lista de dicts {tarefa: valor} sobre as MESMAS tarefas (reamostra tarefas com reposição, pareado)
    tarefas = sorted(set.intersection(*[set(v) for v in vetores]))
    rng, saidas = random.Random(semente), []
    for _ in range(repeticoes):
        amostra = [rng.choice(tarefas) for _ in tarefas]
        saidas.append(estatistica([[v[t] for t in amostra] for v in vetores]))
    saidas.sort()
    # intervalo de 95%: percentis 2,5% e 97,5% das estatísticas reamostradas
    return saidas[int(0.025 * len(saidas))], saidas[int(0.975 * len(saidas)) - 1]


def resumo(args):
    saida = Path(args.saida)
    dados = carregar(saida)
    if not dados:
        print("nenhum resultado em", saida)
        return

    # --- tabela principal: uma linha por configuração ---
    linhas = [
        "# Nível 2: agente completo (25 tarefas)\n",
        "| configuração | execuções | TaskSuccessRate (IC 95%) | por repetição | FirstAttempt | iterações | chamadas ao LLM | s/tarefa | erros de infraestrutura | usou o especialista |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    vetores, json_saida = {}, {}
    for c in sorted(dados):
        todas = dados[c]
        # execuções com erro de infraestrutura (timeout, rede) ficam fora das métricas e são contadas à parte
        validas = [r for r in todas if not r["erro_llm"]]
        v = por_tarefa(validas)
        vetores[c] = v
        ic = bootstrap([v], lambda m: media(m[0]))
        reps = sorted({r["rep"] for r in validas})
        por_rep = " / ".join(f"{100 * media([bool(r['correto']) for r in validas if r['rep'] == k]):.0f}%" for k in reps)
        # FirstAttempt: correta sem nenhum reparo
        primeira = media([bool(r["correto"]) and r["reparos"] == 0 for r in validas])
        especialista = f"{sum(r['usou_especialista'] for r in todas)}/{len(todas)}" if c == "B" else "-"
        taxa = media(list(v.values()))
        linhas.append(
            f"| {NOMES.get(c, c)} | {len(validas)} (+{len(todas) - len(validas)} com erro de infra) | **{100 * taxa:.1f}%** ({100 * ic[0]:.0f} a {100 * ic[1]:.0f}) | {por_rep} | {100 * primeira:.0f}% | "
            f"{media([r['iteracoes'] for r in validas]):.1f} | {media([r['chamadas'] for r in validas]):.1f} | {media([r['segundos'] for r in validas]):.0f} | {sum(r['erro_llm'] > 0 for r in todas)} | {especialista} |"
        )
        json_saida[c] = {
            "execucoes": len(validas),
            "erros_de_infra": len(todas) - len(validas),
            "task_success_rate": taxa,
            "ic95": ic,
            "first_attempt": primeira,
        }

    # --- diferenças em relação ao A (pareadas: as mesmas tarefas nas duas configurações) ---
    if "A" in vetores:
        linhas += [
            "",
            "## Diferenças em relação ao A (pareadas por tarefa; bootstrap sobre as 25 tarefas)\n",
            "| comparação | diferença em pontos (IC 95%) | leitura |",
            "|---|---|---|",
        ]
        for c in ("B", "C"):
            if c in vetores:
                dif = lambda m: media(m[1]) - media(m[0])
                ic = bootstrap([vetores["A"], vetores[c]], dif)
                d = 100 * dif([list(vetores["A"].values()), list(vetores[c].values())]) if set(vetores["A"]) == set(vetores[c]) else float("nan")
                leitura = "intervalo contém 0: não dá para afirmar diferença" if ic[0] <= 0 <= ic[1] else "intervalo não contém 0"
                linhas.append(f"| {c} − A | {d:+.1f} ({100 * ic[0]:+.0f} a {100 * ic[1]:+.0f}) | {leitura} |")
                json_saida[f"{c}_menos_A"] = {"diferenca": d, "ic95": ic}

    # --- por tipo de tarefa: corretas / execuções válidas ---
    linhas += ["", "## Por tipo de tarefa (corretas / execuções válidas)\n"]
    tipos = sorted({r["tipo"] for c in dados for r in dados[c]})
    linhas += ["| tipo | " + " | ".join(sorted(dados)) + " |", "|---|" + "---|" * len(dados)]
    for t in tipos:
        linhas.append(
            f"| {t} | "
            + " | ".join(
                f"{sum(bool(r['correto']) for r in dados[c] if r['tipo'] == t and not r['erro_llm'])}/{sum(1 for r in dados[c] if r['tipo'] == t and not r['erro_llm'])}"
                for c in sorted(dados)
            )
            + " |"
        )

    texto = "\n".join(linhas) + "\n"
    (saida / "resumo.md").write_text(texto, encoding="utf-8")
    (saida / "resumo.json").write_text(json.dumps(json_saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print(texto)


# ---------------------------------------------------------------------------------------------
# Linha de comando
# ---------------------------------------------------------------------------------------------

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rodar")
    r.add_argument("saida")
    r.add_argument("--repeticoes", type=int, default=1)
    r.add_argument("--configs", nargs="+", default=["A", "B", "C"], choices=["A", "B", "C"])
    r.add_argument("--conjuntos", nargs="+", default=["facil", "dificil"], choices=["facil", "dificil"])
    r.add_argument("--tarefas", nargs="*", default=[])
    r.add_argument("--paralelo", type=int, default=3)

    s = sub.add_parser("resumo")
    s.add_argument("saida")

    args = p.parse_args()
    rodar(args) if args.cmd == "rodar" else resumo(args)


if __name__ == "__main__":
    main()

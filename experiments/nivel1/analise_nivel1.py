"""Análise estatística do Nível 1, sobre as saídas já gravadas (nada é gerado de novo).

Uso: python experiments/nivel1/analise_nivel1.py [pasta_nivel1]

Duas métricas, porque a nota depende de como se tratam os casos que não dá para julgar:
  A (a pré-definida): corretos / (corretos + errados). Casos inavaliáveis e planos ilegíveis ficam FORA do denominador.
  B (estrita):         média, por prompt, de corretos / (todos os casos escritos). Inavaliável conta como não correto
                       e um plano ilegível (formato inválido) vale 0. Não deixa o modelo ganhar por ter casos descartados.
Se as duas métricas levam à mesma conclusão, a conclusão é robusta ao tratamento dos casos descartados.

Intervalos: bootstrap por CLUSTER (a tarefa: os prompts e os casos de uma mesma tarefa não são independentes),
5000 reamostras.
Comparações: PAREADAS. Os modelos responderam aos mesmos prompts, então cada reamostra usa as mesmas tarefas para
os dois modelos e o intervalo é o da DIFERENÇA (sobreposição de intervalos individuais não é um teste).
"""
import json
import random
import sys
from pathlib import Path

PASTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "execucoes" / "nivel1"

# nome mostrado na análise -> prefixo dos arquivos em PASTA
MODELOS = {
    "base": "q15_base_schema",
    "base+2 exemplos": "q15_base_2exemplos_schema",
    "ajustado (3 épocas)": "q15_ajustado3ep_schema",
    "ajustado (melhor ponto)": "q15_ajustadomelhor_schema",
    "14B": "q14b_schema",
}

# pares comparados (o primeiro menos o segundo)
COMPARACOES = [
    ("ajustado (3 épocas)", "base"),
    ("ajustado (3 épocas)", "base+2 exemplos"),
    ("ajustado (3 épocas)", "14B"),
    ("ajustado (melhor ponto)", "ajustado (3 épocas)"),
]
REPETICOES = 5000


# ---------- ler as avaliações e calcular as métricas ----------

def carregar(nome):
    # {conjunto: {cluster: {"c","e","i" (casos), "n" prompts, "soma_b" (soma das notas B por prompt)}}}
    saida = {"real": {}, "sintetico": {}}
    for linha in (PASTA / f"{nome}_avaliacao.jsonl").read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        p = json.loads(linha)
        notas = [c["nota"] for c in p["casos"]]
        c, e, i = notas.count("correto"), notas.count("errado"), notas.count("inavaliavel")
        # nota B do prompt: corretos / todos os casos; plano ilegível ou sem casos vale 0
        nota_b = (c / len(notas)) if (p["formato_ok"] and notas) else 0.0
        d = saida[p["conjunto"]].setdefault(p["tarefa"], {"c": 0, "e": 0, "i": 0, "n": 0, "soma_b": 0.0})
        d["c"] += c
        d["e"] += e
        d["i"] += i
        d["n"] += 1
        d["soma_b"] += nota_b
    return saida


def metrica(clusters, nome):
    # "A": corretos / (corretos + errados); "B": média das notas B dos prompts
    if nome == "A":
        c, e = sum(x["c"] for x in clusters), sum(x["e"] for x in clusters)
        return c / (c + e) if c + e else None
    return sum(x["soma_b"] for x in clusters) / sum(x["n"] for x in clusters)


def intervalo(valores):
    # percentis 2,5 e 97,5 dos valores reamostrados (IC de 95%)
    valores = sorted(v for v in valores if v is not None)
    return valores[int(0.025 * len(valores))], valores[int(0.975 * len(valores)) - 1]


def bootstrap(dados_por_modelo, nomes, conjunto, metrica_nome, semente=0):
    # reamostra TAREFAS (iguais para todos os modelos) e devolve, por reamostra, o valor da métrica de cada modelo
    tarefas = sorted(set.intersection(*[set(dados_por_modelo[n][conjunto]) for n in nomes]))
    rng, saidas = random.Random(semente), []
    for _ in range(REPETICOES):
        amostra = [rng.choice(tarefas) for _ in tarefas]
        saidas.append([
            metrica([dados_por_modelo[n][conjunto][t] for t in amostra], metrica_nome)
            for n in nomes
        ])
    return tarefas, saidas


# ---------- montar o relatório (analise.md) ----------

def principal():
    dados = {nome: carregar(arq) for nome, arq in MODELOS.items()}
    linhas = [
        "# Análise estatística do Nível 1\n",
        "Métrica **A**: corretos ÷ (corretos + errados), descartados fora (a pré-definida). "
        "Métrica **B**: estrita, por prompt; inavaliável conta como não correto e plano ilegível vale 0.",
        "IC 95% por bootstrap sobre tarefas (5000 reamostras). Comparações pareadas: mesmas tarefas nos dois modelos.\n",
    ]

    for conjunto, titulo in (
        ("real", "Teste real (60 prompts, 25 tarefas)"),
        ("sintetico", "Teste sintético (80 prompts, 80 exercícios)"),
    ):
        # tabela 1: cada modelo, com as duas métricas e o IC
        nomes = list(MODELOS)
        _, amostras = bootstrap(dados, nomes, conjunto, "A")
        _, amostras_b = bootstrap(dados, nomes, conjunto, "B")
        linhas += [f"## {titulo}\n", "| modelo | A: valores corretos (IC 95%) | B estrita (IC 95%) |", "|---|---|---|"]
        for k, n in enumerate(nomes):
            todas = list(dados[n][conjunto].values())
            a, b = metrica(todas, "A"), metrica(todas, "B")
            ia, ib = intervalo([s[k] for s in amostras]), intervalo([s[k] for s in amostras_b])
            linhas.append(
                f"| {n} | {100 * a:.1f}% ({100 * ia[0]:.0f} a {100 * ia[1]:.0f}) | "
                f"{100 * b:.1f}% ({100 * ib[0]:.0f} a {100 * ib[1]:.0f}) |"
            )

        # tabela 2: diferenças pareadas entre modelos
        linhas += [
            "",
            "Diferenças pareadas (em pontos percentuais; positivo = o primeiro é melhor):\n",
            "| comparação | A: diferença (IC 95%) | A: P(dif ≤ 0) | B: diferença (IC 95%) | B: P(dif ≤ 0) |",
            "|---|---|---|---|---|",
        ]
        for x, y in COMPARACOES:
            cel = []
            for nome_metrica in ("A", "B"):
                _, am = bootstrap(dados, [x, y], conjunto, nome_metrica)
                difs = [s[0] - s[1] for s in am if s[0] is not None and s[1] is not None]
                todas_x, todas_y = list(dados[x][conjunto].values()), list(dados[y][conjunto].values())
                obs = metrica(todas_x, nome_metrica) - metrica(todas_y, nome_metrica)
                lo, hi = intervalo(difs)
                p = sum(d <= 0 for d in difs) / len(difs)
                cel += [f"{100 * obs:+.1f} ({100 * lo:+.0f} a {100 * hi:+.0f})", f"{p:.3f}"]
            linhas.append(f"| {x} − {y} | " + " | ".join(cel) + " |")
        linhas.append("")

    # planos totalmente corretos: todos os casos avaliáveis certos, sem nenhum errado
    linhas += [
        "## Planos com TODOS os casos corretos (um caso errado ou inavaliável tira o plano da conta; "
        "denominador = todos os prompts)\n",
        "| modelo | real | sintético |",
        "|---|---|---|",
    ]
    for nome, arq in MODELOS.items():
        celulas = []
        for conjunto in ("real", "sintetico"):
            total = limpos = 0
            for linha in (PASTA / f"{arq}_avaliacao.jsonl").read_text(encoding="utf-8").splitlines():
                p = json.loads(linha)
                if p["conjunto"] != conjunto:
                    continue
                total += 1
                notas = [c["nota"] for c in p["casos"]]
                # TODOS os casos corretos (inavaliável não vale)
                limpos += bool(p["formato_ok"] and notas and all(n == "correto" for n in notas))
            celulas.append(f"{limpos}/{total} ({100 * limpos / total:.0f}%)")
        linhas.append(f"| {nome} | {celulas[0]} | {celulas[1]} |")

    texto = "\n".join(linhas) + "\n"
    (PASTA / "analise.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    principal()

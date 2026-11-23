"""Liga o Nível 1 ao Nível 2: o plano de testes que o agente REALMENTE usou em cada execução, pontuado pelo oráculo,
e o resultado da tarefa. Responde: quando o plano tinha valores errados, o agente falhou mais?

Uso: python experiments/analise_nivel2_planos.py <pasta_do_nivel2> [saida.md]
Lê <pasta>/<A|B|C>_r<n>_<facil|dificil>/tarefa_NN/.minicode/test_plan.md (o plano final gravado pelo agente) e resultados.json.
"""
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import oraculo

ITEM = re.compile(r"^\d+\.\s*Crit[eé]rio:\s*(?P<c>.*?)\n\s*-\s*entrada:\s*(?P<e>.*?)\n\s*-\s*esperado:\s*(?P<x>.*?)(?=\n\d+\.\s*Crit[eé]rio:|\Z)", re.S | re.M)


def ler_plano(arquivo):
    texto = Path(arquivo).read_text(encoding="utf-8")
    return [{"criterio": m["c"].strip(), "entrada": m["e"].strip(), "esperado": m["x"].strip()} for m in ITEM.finditer(texto)]


def media(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    base = Path(sys.argv[1])
    linhas = []
    for pasta in sorted(base.glob("*_r*_*")):
        if not (pasta / "resultados.json").is_file():
            continue
        config, _, conjunto = pasta.name.split("_")
        if config == "C":
            continue   # sem plano de testes
        for r in json.loads((pasta / "resultados.json").read_text(encoding="utf-8")):
            plano = pasta / f"tarefa_{r['id']:02d}" / ".minicode" / "test_plan.md"
            if not plano.is_file():
                continue
            casos = ler_plano(plano)
            notas = oraculo.avaliar_casos(conjunto, r["id"], casos) if casos else []
            linhas.append({"config": config, "conjunto": conjunto, "id": r["id"], "nome": r["nome"], "correto": bool(r["correto"]),
                           "reparos": r["reparos"], "casos": len(casos), "certos": notas.count("correto"), "errados": notas.count("errado"),
                           "inavaliaveis": notas.count("inavaliavel")})
    saida = ["# Qualidade do plano de testes que o agente usou × resultado da tarefa\n",
             "O plano final gravado pelo agente (`test_plan.md`) pontuado pelo oráculo. \"Plano com erro\" = pelo menos um caso com valor esperado errado.\n",
             "| configuração | execuções | valores corretos no plano | planos sem nenhum erro | tarefas corretas com plano SEM erro | tarefas corretas com plano COM erro |", "|---|---|---|---|---|---|"]
    for c in ("A", "B"):
        L = [x for x in linhas if x["config"] == c]
        if not L:
            continue
        certos, errados = sum(x["certos"] for x in L), sum(x["errados"] for x in L)
        sem = [x for x in L if x["errados"] == 0]; com = [x for x in L if x["errados"] > 0]
        saida.append(f"| {c} | {len(L)} | {100 * certos / max(certos + errados, 1):.1f}% ({certos}/{certos + errados}) | {len(sem)}/{len(L)} | "
                     f"{sum(x['correto'] for x in sem)}/{len(sem)} | {sum(x['correto'] for x in com)}/{len(com)} |")
    saida += ["", "## Execuções com plano com erro\n", "| config | tarefa | plano: certos/errados | tarefa correta | reparos |", "|---|---|---|---|---|"]
    for x in sorted((x for x in linhas if x["errados"] > 0), key=lambda x: (x["config"], x["conjunto"], x["id"])):
        saida.append(f"| {x['config']} | {x['conjunto']} {x['id']:02d} {x['nome']} | {x['certos']}/{x['errados']} | {'sim' if x['correto'] else '**não**'} | {x['reparos']} |")
    texto = "\n".join(saida) + "\n"
    print(texto)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()

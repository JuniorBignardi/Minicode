"""Pontua o resultado_1.0.json gerado no Colab (modelo base × ajustado) com o oráculo.

NOTA: a avaliação feita no Colab (sem JSON Schema) foi descartada; a avaliação oficial é a de avaliar_endpoint.py.
Do que há neste arquivo, só `pontuar_sintetico` ainda é usado (por avaliar_endpoint.py). O restante (main e
interpretar_leniente) ficou como registro e não faz parte dos resultados finais.

Uso: python experiments/nivel1/avaliar_resultado_colab.py <resultado.json> <saida_prefixo>
Teste real: os 60 prompts das 25 tarefas (referência da tarefa como oráculo).
Teste sintético: os exercícios de exemplos_teste.jsonl (referência de cada exercício).
Cada caso é executado na referência: correto, errado ou inavaliável. Métrica: corretos / (corretos + errados).
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py
sys.path.insert(0, str(RAIZ / "src"))
import avaliar_nivel1 as n1
import oraculo
from minicode.spec.plano_de_testes import criterios_da_spec, validar_plano_de_testes

DADOS = AQUI.parents[1] / "datasets" / "plano_de_testes"   # o dataset versionado no repositório
V3 = DADOS


def pontuar_sintetico(exemplos, registros, respostas):
    # para cada exercício do teste sintético: lê o plano da resposta e confere cada caso na referência DO exercício
    saidas = []
    for e, resposta in zip(exemplos, respostas):
        r = registros[e["tarefa_id"]]
        casos = n1.interpretar(resposta or "")
        criterios = criterios_da_spec(n1.spec_da_mensagem(e["mensagens"][1]["content"]))
        valido = casos is not None and validar_plano_de_testes(criterios, casos)[0]
        notas = []
        if casos:
            # pasta temporária só com a referência do exercício; apagada no fim, mesmo se der erro
            pasta = Path(tempfile.mkdtemp())
            try:
                (pasta / r["arquivo"]).write_text(r["referencia"], encoding="utf-8")
                notas = [
                    oraculo.comparar(oraculo.executar_entrada(pasta, c["entrada"]), c["esperado"])
                    for c in casos
                ]
            finally:
                shutil.rmtree(pasta, ignore_errors=True)
        saidas.append({
            "tarefa": e["tarefa_id"],
            "formato_ok": casos is not None,
            "plano_valido": valido,
            "notas": notas,
            "casos": casos or [],
        })
    return saidas


def main():
    # (não usado nos resultados finais) pontua o JSON que o notebook do Colab gerava
    sys.stdout.reconfigure(encoding="utf-8")
    res = json.load(open(sys.argv[1], encoding="utf-8"))
    prefixo = sys.argv[2]

    # confere que os prompts do Colab são os mesmos dos logs da Parte 1
    entradas = n1.entradas_reais(AQUI.parent / "execucoes" / "diagnostico_14b")
    guardadas = json.load(open(DADOS / "entradas_reais.json", encoding="utf-8"))
    assert len(entradas) == len(guardadas) == len(res["real_ajustado"]), (
        len(entradas), len(guardadas), len(res["real_ajustado"])
    )
    assert all(a["mensagens"] == b["mensagens"] for a, b in zip(entradas, guardadas)), \
        "os prompts do Colab não são os dos logs"
    exemplos = [json.loads(l) for l in open(DADOS / "exemplos_teste.jsonl", encoding="utf-8") if l.strip()]
    registros = {
        r["id"]: r
        for r in (json.loads(l) for l in open(V3 / "registros_teste.jsonl", encoding="utf-8") if l.strip())
    }

    # pontua o teste real (ajustado, base e 14B) e o sintético (ajustado e base)
    todos = {}
    for nome, chave in (("ajustado", "real_ajustado"), ("base", "real_base")):
        it = iter(res[chave])
        todos[f"real_{nome}"] = n1.pontuar(entradas, gerar=lambda m: next(it))
    todos["real_14b"] = n1.pontuar(entradas)
    for nome, chave in (("ajustado", "sintetico_ajustado"), ("base", "sintetico_base")):
        todos[f"sintetico_{nome}"] = pontuar_sintetico(exemplos, registros, res[chave])

    # resumos e notas em JSON
    resumos = {}
    for k, v in todos.items():
        resumos[k] = n1.resumo(v)
        n1.mostrar(k, resumos[k])
    json.dump(resumos, open(prefixo + "_resumo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(
        {k: [{x: y for x, y in r.items() if x != "casos"} for r in v] for k, v in todos.items()},
        open(prefixo + "_notas.json", "w", encoding="utf-8"),
        ensure_ascii=False,
    )

    # versão legível: cada plano com a nota de cada caso
    linhas = ["# Respostas do Colab, lidas e pontuadas\n"]
    for k in ("real_ajustado", "real_base", "sintetico_ajustado", "sintetico_base"):
        chave = {
            "real_ajustado": "real_ajustado",
            "real_base": "real_base",
            "sintetico_ajustado": "sintetico_ajustado",
            "sintetico_base": "sintetico_base",
        }[k]
        linhas.append(f"\n## {k}\n")
        for i, (r, texto) in enumerate(zip(todos[k], res[chave])):
            linhas.append(
                f"### {i}: {r['tarefa']} | formato {'ok' if r['formato_ok'] else 'INVÁLIDO'} | "
                f"plano {'válido' if r['plano_valido'] else 'inválido'} | "
                f"notas: {r['notas'].count('correto')} corretos, {r['notas'].count('errado')} errados, "
                f"{r['notas'].count('inavaliavel')} inavaliáveis"
            )
            casos = n1.interpretar(texto or "") or []
            for c, n in zip(casos, r["notas"]):
                linhas.append(f"- [{n}] `{c['entrada'][:110]}` → `{str(c['esperado'])[:70]}`")
            if not casos:
                linhas.append("```\n" + (texto or "")[:500] + "\n```")
    Path(prefixo + "_legivel.md").write_text("\n".join(linhas), encoding="utf-8")


if __name__ == "__main__":
    main()


# ---------- código não usado (fica só como registro) ----------
# Definida depois do `if __name__`, então nem existe quando o arquivo roda como script; nada a importa.

def interpretar_leniente(texto):
    # dá a melhor chance ao modelo base: aceita lista solta e cerca de código;
    # só usa casos em que entrada e esperado são texto
    inicio_o, inicio_l = texto.find("{"), texto.find("[")
    candidatos = [(i, f) for i, f in ((inicio_o, "{"), (inicio_l, "[")) if i >= 0]
    if not candidatos:
        return None
    for i, f in sorted(candidatos):
        fim = texto.rfind("}" if f == "{" else "]")
        try:
            obj = json.loads(texto[i:fim + 1])
        except Exception:
            continue
        lista = obj.get("casos") if isinstance(obj, dict) else obj
        if isinstance(lista, list):
            return [
                c for c in lista
                if isinstance(c, dict) and isinstance(c.get("entrada"), str) and isinstance(c.get("esperado"), str)
            ]
    return None

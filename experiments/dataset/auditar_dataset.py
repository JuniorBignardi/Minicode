"""Auditoria do dataset de plano de testes (treino, validação e teste).

Etapas: 1) estrutura, 2) estatísticas, 3) duplicatas (exatas e parecidas), 4) correção dos valores esperados
(reexecuta a solução de referência), 5) contaminação entre treino e validação/teste, 6) classificação de cada
exemplo em aprovado / revisar / rejeitado.

Uso: python auditar_dataset.py [pasta_do_dataset]   (padrão: ../execucoes/dataset_v2)
Gera auditoria.md e auditoria.json na pasta do dataset.
"""
import json
import re
import sys
import collections
import statistics
from ast import parse, Expression, Expr
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PASTA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "execucoes" / "dataset_v2"
CONJUNTOS = ["treino", "validacao", "teste"]

# tags do formato do professor que não podem sobrar dentro de um prompt
TAGS = re.compile(r"</?(casos|plano|referencia|pedido|arquivo|especificacao|entradas)>")

# palavras comuns de cada língua, para detectar texto em inglês
INGLES = re.compile(r"\b(the|and|with|for|to|of|is|if|that|each|when|in)\b", re.I)
PORTUGUES = re.compile(r"\b(o|a|de|para|com|que|se|um|uma|e|do|da|em|os|as)\b", re.I)

# exceções que quase sempre indicam erro da referência, e não um comportamento pedido
EXCECOES_ESTRANHAS = {
    "StopIteration", "NameError", "AttributeError", "UnboundLocalError", "ZeroDivisionError",
    "RecursionError", "ModuleNotFoundError", "ImportError", "SyntaxError", "AssertionError",
}

# acima destes valores, dois pedidos são considerados parecidos
LIMITE_PARECIDO_PEDIDO = 0.45      # TF-IDF dos pedidos (os pedidos são parafraseados: o máximo real é ~0,6)
LIMITE_PARECIDO_EMBEDDING = 0.93   # embeddings multilíngues dos pedidos


def ler(caminho):
    return [json.loads(l) for l in open(caminho, encoding="utf-8") if l.strip()]


# Executa a entrada na referência e devolve o repr do resultado, ou o nome da exceção levantada.
# O último comando da entrada é tratado como a expressão cujo valor é conferido.
def executar(referencia, entrada):
    espaco = {}
    try:
        exec(referencia, espaco)
        arvore = parse(entrada)
        ultimo = Expression(arvore.body.pop().value) if arvore.body and isinstance(arvore.body[-1], Expr) else None
        exec(compile(arvore, "<x>", "exec"), espaco)
        return repr(eval(compile(ultimo, "<x>", "eval"), espaco)) if ultimo else "None"
    except BaseException as erro:
        return type(erro).__name__


def nomes_definidos(referencia):
    return set(re.findall(r"^(?:def|class) (\w+)", referencia, re.M)) - {"__init__"}


def criterios_da_spec(spec):
    achou = re.search(r"## Acceptance Criteria\n(.*)", spec, re.S)
    return [l[2:].strip() for l in achou.group(1).split("\n") if l.startswith("- ")] if achou else []


def main():
    registros = {n: ler(PASTA / f"registros_{n}.jsonl") for n in CONJUNTOS}
    exemplos = {n: ler(PASTA / f"exemplos_{n}.jsonl") for n in CONJUNTOS}
    problemas = collections.defaultdict(lambda: collections.defaultdict(list))   # id -> etiqueta -> detalhes
    linhas = ["# Auditoria do dataset\n"]

    # anota um problema de um exemplo; "rejeitar" tira o exemplo, "revisar" só pede uma olhada
    def marca(conjunto, id_, nivel, etiqueta, detalhe=""):
        problemas[(conjunto, id_)][(nivel, etiqueta)].append(detalhe)

    # ---------- 1. estrutura ----------
    # cada exemplo tem as chaves certas, system+user, resposta em JSON, um caso por critério da spec etc.
    linhas.append("## 1. Estrutura\n")
    for n in CONJUNTOS:
        ruins = 0
        if len(registros[n]) != len(exemplos[n]):
            linhas.append(
                f"- {n}: registros ({len(registros[n])}) e exemplos ({len(exemplos[n])}) com tamanhos diferentes"
            )
        reg = {r["id"]: r for r in registros[n]}
        for e in exemplos[n]:
            id_ = e["tarefa_id"]
            if set(e) != {"tarefa_id", "modelo", "mensagens", "resposta"}:
                marca(n, id_, "rejeitar", "chaves_do_exemplo")
                ruins += 1
                continue
            if [m["role"] for m in e["mensagens"]] != ["system", "user"]:
                marca(n, id_, "rejeitar", "papeis_das_mensagens")
            texto = e["mensagens"][1]["content"]
            try:
                casos = json.loads(e["resposta"])["casos"]
            except Exception:
                marca(n, id_, "rejeitar", "resposta_nao_e_json")
                continue
            if not casos:
                marca(n, id_, "rejeitar", "sem_casos")
            if "�" in texto or "�" in e["resposta"]:
                marca(n, id_, "rejeitar", "caractere_corrompido")
            if TAGS.search(texto):
                marca(n, id_, "rejeitar", "restos_de_tag_no_prompt")
            for c in casos:
                if set(c) != {"criterio", "entrada", "esperado"} or any(
                    not isinstance(v, str) or not v.strip() for v in c.values()
                ):
                    marca(n, id_, "rejeitar", "caso_mal_formado")
            # os critérios da spec (parte do prompt antes de "Plano:") têm que ser exatamente os dos casos
            criterios = set(criterios_da_spec(texto.split("Plano:")[0]))
            cobertos = {c["criterio"] for c in casos}
            if criterios != cobertos:
                marca(
                    n, id_, "rejeitar", "criterios_da_spec_diferentes_dos_casos",
                    f"so_spec={len(criterios - cobertos)} so_casos={len(cobertos - criterios)}",
                )
            ing = len(INGLES.findall(texto))
            por = len(PORTUGUES.findall(texto))
            if ing >= 8 and ing > por * 0.5:
                marca(n, id_, "revisar", "texto_em_ingles")
        linhas.append(f"- {n}: {len(exemplos[n])} exemplos, estrutura verificada")

    # ---------- 2. estatísticas ----------
    linhas.append("\n## 2. Estatísticas\n")
    linhas.append(
        "| conjunto | exemplos | casos/ex (mín/média/máx) | casos de exceção | tamanho do prompt (média/máx, chars) | resposta (média/máx, chars) |\n|---|---|---|---|---|---|"
    )
    for n in CONJUNTOS:
        por_ex, exc, total, tp, tr = [], 0, 0, [], []
        for e in exemplos[n]:
            casos = json.loads(e["resposta"])["casos"]
            por_ex.append(len(casos))
            total += len(casos)
            exc += sum(bool(re.fullmatch(r"[A-Z]\w*(Error|Iteration|Exception)", c["esperado"].strip())) for c in casos)
            tp.append(len(e["mensagens"][1]["content"]))
            tr.append(len(e["resposta"]))
            for c in casos:
                if len(c["esperado"]) > 600:
                    marca(n, e["tarefa_id"], "revisar", "esperado_muito_longo", str(len(c["esperado"])))
        linhas.append(
            f"| {n} | {len(por_ex)} | {min(por_ex)}/{statistics.mean(por_ex):.1f}/{max(por_ex)} | {exc / total:.0%} "
            f"| {statistics.mean(tp):.0f}/{max(tp)} | {statistics.mean(tr):.0f}/{max(tr)} |"
        )
    por_modelo = collections.Counter(e["modelo"] for e in exemplos["treino"])
    linhas.append("\nProfessores (treino): " + ", ".join(f"{m}: {q}" for m, q in por_modelo.items()))

    # ---------- 3. duplicatas ----------
    linhas.append("\n## 3. Duplicatas\n")

    # prompts idênticos (em qualquer conjunto)
    vistos = collections.defaultdict(list)
    for n in CONJUNTOS:
        for e in exemplos[n]:
            vistos[e["mensagens"][1]["content"]].append((n, e["tarefa_id"]))
    exatas = [v for v in vistos.values() if len(v) > 1]
    linhas.append(f"- prompts idênticos: {len(exatas)}")
    for v in exatas:
        for n, id_ in v:
            marca(n, id_, "rejeitar", "prompt_duplicado", str(v))

    # casos com a mesma entrada e o mesmo esperado dentro de um exercício
    repetidos_no_exemplo = 0
    for n in CONJUNTOS:
        for r in registros[n]:
            c = collections.Counter((x["entrada"], x["esperado"]) for x in r["casos"])
            if any(q > 1 for q in c.values()):
                repetidos_no_exemplo += 1
                marca(n, r["id"], "revisar", "caso_repetido_no_exemplo")
    linhas.append(f"- exemplos com caso repetido (mesma entrada e esperado): {repetidos_no_exemplo}")

    # pedidos parecidos: matriz de similaridade por TF-IDF (sempre) e por embeddings (se a biblioteca existir)
    todos = [(n, r) for n in CONJUNTOS for r in registros[n]]
    pedidos = [r["pedido"] for _, r in todos]
    tf = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True).fit_transform(pedidos)
    sim_tf = cosine_similarity(tf)
    np.fill_diagonal(sim_tf, 0)

    sim_emb = None
    try:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        emb = modelo.encode(pedidos, normalize_embeddings=True, show_progress_bar=False)
        sim_emb = emb @ emb.T
        np.fill_diagonal(sim_emb, 0)
        linhas.append("- similaridade semântica: embeddings multilíngues (paraphrase-multilingual-MiniLM-L12-v2) + TF-IDF")
    except Exception as erro:
        linhas.append(f"- similaridade semântica indisponível ({type(erro).__name__}); só TF-IDF")

    # índice: nome de função/classe -> exercícios que o definem
    nomes = [nomes_definidos(r["referencia"]) for _, r in todos]
    mesmos_nomes = collections.defaultdict(list)
    for i, ns in enumerate(nomes):
        for nome in ns:
            mesmos_nomes[nome].append(i)

    # diversidade: arquivos que se repetem no treino (um bug de referência tende a se repetir neles)
    por_arquivo = collections.Counter(r["arquivo"] for n, r in todos if n == "treino")
    familias = {a: q for a, q in por_arquivo.items() if q >= 2}
    linhas.append(
        f"- diversidade: {len(por_arquivo)} arquivos distintos no treino; {len(familias)} se repetem, "
        f"cobrindo {sum(familias.values())} dos {len(exemplos['treino'])} exemplos "
        "(famílias do mesmo tema: um bug de referência tende a se repetir nelas)"
    )
    for a, q in sorted(familias.items(), key=lambda x: -x[1])[:8]:
        linhas.append(f"  - `{a}`: {q}")

    # compara todos os pares de exercícios: parecidos dentro do mesmo conjunto e entre conjuntos diferentes
    pares_treino = pares_contaminacao = 0
    vistos_par = set()
    for i in range(len(todos)):
        for j in range(i + 1, len(todos)):
            parecidos = sim_tf[i, j] >= LIMITE_PARECIDO_PEDIDO or (
                sim_emb is not None and sim_emb[i, j] >= LIMITE_PARECIDO_EMBEDDING
            )
            if not parecidos:
                continue
            (ni, ri), (nj, rj) = todos[i], todos[j]
            detalhe = f"{ri['id']}~{rj['id']} tf={sim_tf[i, j]:.2f}" + (
                f" emb={sim_emb[i, j]:.2f}" if sim_emb is not None else ""
            )
            if ni != nj:
                pares_contaminacao += 1
                marca(ni, ri["id"], "revisar", "parecido_com_outro_conjunto", detalhe + f" ({nj})")
                marca(nj, rj["id"], "revisar", "parecido_com_outro_conjunto", detalhe + f" ({ni})")
            else:
                pares_treino += 1
                marca(ni, ri["id"], "revisar", "parecido_no_mesmo_conjunto", detalhe)
                marca(nj, rj["id"], "revisar", "parecido_no_mesmo_conjunto", detalhe)
            vistos_par.add((i, j))
    linhas.append(f"- pares de pedidos parecidos dentro do mesmo conjunto: {pares_treino}")

    # ---------- 5. contaminação ----------
    # (no código vem antes da seção 4 porque reaproveita as comparações de pares feitas acima)
    linhas.append("\n## 5. Contaminação entre conjuntos\n")
    linhas.append(f"- pares de pedidos parecidos entre conjuntos diferentes: {pares_contaminacao}")

    # a mesma função/classe aparecendo no treino e na validação ou no teste
    compartilhados = []
    for nome, idxs in mesmos_nomes.items():
        conjuntos = {todos[i][0] for i in idxs}
        if "treino" in conjuntos and len(conjuntos) > 1 and not nome.startswith("_"):
            compartilhados.append((nome, [(todos[i][0], todos[i][1]["id"]) for i in idxs]))
            for i in idxs:
                if todos[i][0] != "treino":
                    marca(todos[i][0], todos[i][1]["id"], "revisar", "mesma_funcao_do_treino", nome)
    linhas.append(f"- nomes de função/classe que aparecem no treino e em validação/teste: {len(compartilhados)}")
    for nome, onde in compartilhados[:15]:
        linhas.append(f"  - `{nome}`: {onde}")

    # entradas de teste (compridas) que são idênticas a alguma do treino
    entradas_treino = {c["entrada"] for r in registros["treino"] for c in r["casos"]}
    vazadas = 0
    for n in ["validacao", "teste"]:
        for r in registros[n]:
            comuns = [c for c in r["casos"] if c["entrada"] in entradas_treino and len(c["entrada"]) > 25]
            if comuns:
                vazadas += len(comuns)
                marca(n, r["id"], "revisar", "entrada_igual_a_do_treino", f"{len(comuns)} caso(s)")
    linhas.append(
        f"- casos de validação/teste com entrada idêntica a uma do treino (entradas com mais de 25 caracteres): {vazadas}"
    )

    # ---------- 4. correção (oráculo) ----------
    # reexecuta cada caso na referência e compara com o `esperado` gravado
    linhas.append("\n## 4. Correção dos valores esperados\n")
    divergentes = estranhas = sem_executar = 0
    for n in CONJUNTOS:
        for r in registros[n]:
            for c in r["casos"]:
                esperado = c["esperado"].strip()
                if esperado in EXCECOES_ESTRANHAS and esperado not in r["pedido"] + r["especificacao"]:
                    estranhas += 1
                    marca(n, r["id"], "rejeitar", "excecao_estranha_como_esperado", f"{c['entrada'][:60]} => {esperado}")
                if "sleep" in c["entrada"]:
                    sem_executar += 1
                    continue
                obtido = executar(r["referencia"], c["entrada"])
                if obtido != esperado:
                    divergentes += 1
                    marca(
                        n, r["id"], "rejeitar", "esperado_diferente_da_referencia",
                        f"{c['entrada'][:60]}: {esperado[:30]} vs {obtido[:30]}",
                    )
    linhas.append(f"- casos cujo esperado difere do que a referência devolve: {divergentes}")
    linhas.append(f"- casos com exceção estranha como esperado: {estranhas}")
    linhas.append(f"- casos não executados (usam sleep): {sem_executar}")
    linhas.append("- observação: isto confere esperado contra referência; não detecta referência errada (ver revisão humana).")

    # ---------- 6. classificação ----------
    # cada exemplo vira "rejeitado" (algum problema grave), "revisar" (só avisos) ou "aprovado"
    linhas.append("\n## 6. Classificação dos exemplos\n")
    resumo = {}
    saida = {}
    contagem_etiquetas = collections.Counter()
    for n in CONJUNTOS:
        cont = collections.Counter()
        for r in registros[n]:
            ps = problemas.get((n, r["id"]), {})
            niveis = {nivel for (nivel, _) in ps}
            classe = "rejeitado" if "rejeitar" in niveis else "revisar" if "revisar" in niveis else "aprovado"
            cont[classe] += 1
            for (nivel, etiqueta) in ps:
                contagem_etiquetas[(nivel, etiqueta)] += 1
            if ps:
                saida[f"{n}/{r['id']}"] = {
                    "classe": classe,
                    "problemas": {f"{nv}:{et}": ds[:3] for (nv, et), ds in ps.items()},
                }
        resumo[n] = cont
    linhas.append("| conjunto | aprovado | revisar | rejeitado |\n|---|---|---|---|")
    for n in CONJUNTOS:
        linhas.append(f"| {n} | {resumo[n]['aprovado']} | {resumo[n]['revisar']} | {resumo[n]['rejeitado']} |")
    linhas.append("\n| nível | problema | exemplos |\n|---|---|---|")
    for (nivel, etiqueta), q in sorted(contagem_etiquetas.items(), key=lambda x: (x[0][0], -x[1])):
        linhas.append(f"| {nivel} | {etiqueta} | {q} |")

    (PASTA / "auditoria.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    (PASTA / "auditoria.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()

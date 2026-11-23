"""Nível 1 por endpoint: um modelo servido por API (Ollama, vLLM) escreve o plano de testes dos prompts reais e do teste sintético,
e o oráculo pontua.

Uso: python experiments/avaliar_endpoint.py <url_base> <modelo> <nome> [--schema] [--exemplos N] [--threads 3] [--so real|sintetico]
  --schema      pede a resposta no formato JSON Schema do plano de testes, como o agente faz, com temperatura 0,3.
                Sem a flag: sem schema e temperatura 0.
  --exemplos N  põe N exemplos fixos do TREINO (os N primeiros do arquivo) como mensagens de exemplo (few-shot).
A chave vem de MINICODE_PLAN_API_KEY ou MINICODE_API_KEY (servidor local não exige).

Arquivos em experiments/execucoes/nivel1/ (tudo para auditoria):
  <nome>_respostas.jsonl   uma linha por chamada: prompt enviado (mensagens), parâmetros, resposta completa, finish_reason, tokens, segundos
  <nome>_avaliacao.jsonl   uma linha por prompt: cada caso do plano com a nota do oráculo (correto, errado ou inavaliavel)
  <nome>_resumo.json       as métricas
Se o arquivo de respostas já existir, as chamadas feitas são reaproveitadas (dá para continuar depois de uma queda).
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(AQUI.parent / "src"))
import avaliar_nivel1 as n1
import avaliar_resultado_colab as colab
from minicode.llm.esquema import formato_da_resposta
from minicode.spec.plano_de_testes import criterios_da_spec, esquema_plano_de_testes

DADOS = AQUI.parent / "datasets" / "plano_de_testes"   # o dataset versionado no repositório
SAIDA = AQUI / "execucoes" / "nivel1"


def com_exemplos(mensagens, exemplos):
    # few-shot: cada exemplo do treino vira um par (pedido do usuário, resposta certa) antes da pergunta de verdade
    meio = []
    for e in exemplos:
        meio += [e["mensagens"][1], {"role": "assistant", "content": e["resposta"]}]
    return [mensagens[0]] + meio + [mensagens[1]]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("url"); p.add_argument("modelo"); p.add_argument("nome")
    p.add_argument("--schema", action="store_true"); p.add_argument("--exemplos", type=int, default=0)
    p.add_argument("--threads", type=int, default=3); p.add_argument("--so", choices=["real", "sintetico"])
    a = p.parse_args()
    from openai import OpenAI
    chave = os.environ.get("MINICODE_PLAN_API_KEY") or os.environ.get("MINICODE_API_KEY") or "sem-chave"
    cliente = OpenAI(base_url=a.url, api_key=chave, timeout=300, max_retries=2)

    guardadas = json.load(open(DADOS / "entradas_reais.json", encoding="utf-8"))
    entradas = n1.entradas_reais(AQUI / "execucoes" / "diagnostico_14b")
    assert len(entradas) == len(guardadas) and all(x["mensagens"] == y["mensagens"] for x, y in zip(entradas, guardadas))
    teste = [json.loads(l) for l in open(DADOS / "exemplos_teste.jsonl", encoding="utf-8") if l.strip()]
    registros = {r["id"]: r for r in (json.loads(l) for l in open(DADOS / "registros_teste.jsonl", encoding="utf-8") if l.strip())}
    treino = [json.loads(l) for l in open(DADOS / "exemplos_treino.jsonl", encoding="utf-8") if l.strip()]
    fixos = treino[:a.exemplos] if a.exemplos else []

    SAIDA.mkdir(exist_ok=True)
    arquivo = SAIDA / f"{a.nome}_respostas.jsonl"
    salvos = {}
    if arquivo.exists():
        for linha in arquivo.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha); salvos[(d["conjunto"], d["i"])] = d

    trabalho = []
    if a.so != "sintetico":
        trabalho += [("real", i, m["mensagens"]) for i, m in enumerate(guardadas)]
    if a.so != "real":
        trabalho += [("sintetico", i, m["mensagens"]) for i, m in enumerate(teste)]

    def gerar(item):
        conjunto, i, mensagens = item
        if (conjunto, i) in salvos:
            return item, salvos[(conjunto, i)], False
        enviadas = com_exemplos(mensagens, fixos) if fixos else mensagens
        args = {"temperature": 0.3 if a.schema else 0, "max_tokens": 2000}
        if a.schema:
            spec = n1.spec_da_mensagem(mensagens[1]["content"])
            args["response_format"] = formato_da_resposta(esquema_plano_de_testes(criterios_da_spec(spec)), "plano_de_testes")
        ultimo = ""
        for _ in range(2):
            try:
                t0 = time.time()
                r = cliente.chat.completions.create(model=a.modelo, messages=enviadas, **args)
                registro = {"conjunto": conjunto, "i": i, "modelo": a.modelo, "config": a.nome,
                            "parametros": {"temperature": args["temperature"], "max_tokens": args["max_tokens"], "schema": a.schema, "exemplos_no_prompt": a.exemplos},
                            "mensagens_enviadas": enviadas, "resposta": r.choices[0].message.content or "",
                            "finish_reason": r.choices[0].finish_reason,
                            "tokens": {"entrada": getattr(r.usage, "prompt_tokens", None), "saida": getattr(r.usage, "completion_tokens", None)},
                            "segundos": round(time.time() - t0, 1)}
                return item, registro, False
            except Exception as erro:
                ultimo = f"{type(erro).__name__}: {str(erro)[:120]}"
        print("  erro:", conjunto, i, ultimo, flush=True)
        return item, None, True

    inicio, falhas, feitas = time.time(), 0, 0
    with ThreadPoolExecutor(a.threads) as pool, open(arquivo, "a", encoding="utf-8") as saida:
        for item, registro, falhou in pool.map(gerar, trabalho):
            conjunto, i, _ = item
            if registro is not None and (conjunto, i) not in salvos:
                saida.write(json.dumps(registro, ensure_ascii=False) + "\n"); saida.flush()
                salvos[(conjunto, i)] = registro
            falhas += falhou; feitas += 1
            if feitas % 10 == 0:
                print(f"  {feitas}/{len(trabalho)} | {(time.time() - inicio) / 60:.1f} min | falhas de infraestrutura {falhas}", flush=True)

    texto = lambda c, i: salvos[(c, i)]["resposta"] if (c, i) in salvos else ""
    resumos, auditoria = {}, []
    if a.so != "sintetico":
        respostas = [texto("real", i) for i in range(len(guardadas))]
        it = iter(respostas)
        pontuados = n1.pontuar(entradas, gerar=lambda m: next(it))
        resumos["real"] = n1.resumo(pontuados)
        n1.mostrar(f"{a.nome} | real", resumos["real"])
        for i, (r, resp) in enumerate(zip(pontuados, respostas)):
            casos = n1.interpretar(resp) or []
            auditoria.append({"conjunto": "real", "i": i, "tarefa": r["tarefa"], "formato_ok": r["formato_ok"], "plano_valido": r["plano_valido"],
                              "casos": [{**c, "nota": n} for c, n in zip(casos, r["notas"])]})
    if a.so != "real":
        respostas = [texto("sintetico", i) for i in range(len(teste))]
        pontuados = colab.pontuar_sintetico(teste, registros, respostas)
        resumos["sintetico"] = n1.resumo(pontuados)
        n1.mostrar(f"{a.nome} | sintético", resumos["sintetico"])
        for i, r in enumerate(pontuados):
            auditoria.append({"conjunto": "sintetico", "i": i, "tarefa": r["tarefa"], "formato_ok": r["formato_ok"], "plano_valido": r["plano_valido"],
                              "casos": [{**c, "nota": n} for c, n in zip(r["casos"], r["notas"])]})
    resumos["falhas_de_infraestrutura"] = falhas
    resumos["respostas_truncadas"] = sum(1 for d in salvos.values() if d["finish_reason"] == "length")
    (SAIDA / f"{a.nome}_avaliacao.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in auditoria), encoding="utf-8")
    (SAIDA / f"{a.nome}_resumo.json").write_text(json.dumps(resumos, ensure_ascii=False, indent=1), encoding="utf-8")
    print("truncadas por limite de tokens:", resumos["respostas_truncadas"], "| falhas de infraestrutura:", falhas)


if __name__ == "__main__":
    main()

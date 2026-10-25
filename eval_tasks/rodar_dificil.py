import contextlib
import json
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import os
from minicode.agent.orquestrador import rodar_agente

# ablação: MINICODE_ABLACAO="planejar_testes=False,diagnosticar=False" desliga componentes do agente
OPCOES = {}
for par in filter(None, os.environ.get("MINICODE_ABLACAO", "").split(",")):
    nome, valor = par.split("=")
    OPCOES[nome] = int(valor) if valor.isdigit() else valor == "True"
print("opções do agente:", OPCOES or "configuração completa", flush=True)
from minicode.llm.client import chat as chat_real

def chat(mensagens, temperature=0, **kw):
    time.sleep(1)  # pausa entre chamadas: o endpoint é da faculdade
    return chat_real(mensagens, temperature=temperature, **kw)


base = Path(sys.argv[1])
selecao = sys.argv[2:]  # ids opcionais (ex.: 1 5 9)


from tarefas_dificeis import TAREFAS


resultados = []
for t in TAREFAS:
    if selecao and str(t["id"]) not in selecao:
        continue
    raiz = base / f"tarefa_{t['id']:02d}"
    shutil.rmtree(raiz, ignore_errors=True)
    raiz.mkdir(parents=True)
    for caminho, conteudo in t["arquivos"].items():
        (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
        (raiz / caminho).write_text(conteudo, encoding="utf-8")

    inicio = time.time()
    with open(raiz / "saida.log", "w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        execucao = rodar_agente(t["tarefa"], raiz, chat, **OPCOES)
    duracao = time.time() - inicio

    eventos = Counter()
    for linha in (raiz / ".minicode" / "actions.jsonl").read_text(encoding="utf-8").splitlines():
        eventos[json.loads(linha)["tipo"]] += 1

    try:
        correto = t["verificar"](raiz) if execucao.estado == "DONE" else False
    except Exception as erro:
        correto = False

    r = dict(id=t["id"], tipo=t["tipo"], nome=t["nome"], estado=execucao.estado,
             correto=correto, reparos=execucao.tentativas, chamadas=execucao.chamadas_llm,
             iteracoes=execucao.iteracoes, segundos=round(duracao),
             problemas={k: v for k, v in eventos.items()
                        if k in ("formato_invalido", "ferramenta_proibida", "acao_repetida",
                                 "escrita_protegida", "finish_recusado", "limite_de_leituras",
                                 "documento_invalido")})
    resultados.append(r)
    print(f"[{t['id']:02d}] {t['tipo']:12} {t['nome']:20} -> {r['estado']:6} correto={correto} reparos={r['reparos']} chamadas={r['chamadas']} {r['segundos']}s {r['problemas']}", flush=True)

(base / "resultados.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
feitas = len(resultados)
concluidas = sum(r["estado"] == "DONE" for r in resultados)
corretas = sum(r["correto"] for r in resultados)
primeira = sum(r["correto"] and r["reparos"] == 0 for r in resultados)
print("\n===== MÉTRICAS =====")
print(f"tarefas concluídas (DONE, testes do agente passaram): {concluidas}/{feitas}")
print(f"TaskSuccessRate (corretas no verificador oculto):     {corretas}/{feitas} = {100 * corretas / max(feitas, 1):.0f}%")
print(f"FirstAttemptSuccess (corretas sem nenhum reparo):     {primeira}/{feitas} = {100 * primeira / max(feitas, 1):.0f}%")
print(f"AverageIterations:                                    {sum(r['iteracoes'] for r in resultados) / max(feitas, 1):.1f}")
print(f"AverageLLMCalls:                                      {sum(r['chamadas'] for r in resultados) / max(feitas, 1):.1f}")
print("\npor tipo (corretas/total):")
for tipo in sorted({r["tipo"] for r in resultados}):
    do_tipo = [r for r in resultados if r["tipo"] == tipo]
    print(f"  {tipo:14} {sum(r['correto'] for r in do_tipo)}/{len(do_tipo)}")

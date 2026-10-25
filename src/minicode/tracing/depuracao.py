# DEBUG: todo este módulo é depuração temporária.
# Para remover depois: apagar este arquivo, os atributos "depurar" e "seq_debug" da Execucao
# e as linhas marcadas com "# DEBUG" (fases.py, orquestrador.py).
#
# Liga com MINICODE_DEBUG=1 (ou rodar_agente(..., depurar=True)) e grava, em
# <projeto>/.minicode/debug.jsonl, uma linha por evento com o conteúdo COMPLETO:
# as mensagens enviadas a cada chamada à LLM, as respostas, os resultados das ferramentas,
# a saída inteira dos testes e as mensagens de reparo.

import json
import os
from datetime import datetime
from pathlib import Path


def depuracao_ligada():
    return os.environ.get("MINICODE_DEBUG") == "1"


def iniciar_depuracao(raiz):
    (Path(raiz) / ".minicode" / "debug.jsonl").write_text("", encoding="utf-8")


def instantaneo(execucao):
    # fotografia do que o programa sabe neste momento
    return {
        "iteracoes": execucao.iteracoes,
        "chamadas_llm": execucao.chamadas_llm,
        "tentativas": execucao.tentativas,
        "testes_passaram": execucao.testes_passaram,
        "revisoes": dict(execucao.revisoes),
        "arquivos_alterados": list(execucao.arquivos_alterados),
        "arquivos_protegidos": list(execucao.arquivos_protegidos),
        "arquivos_exigidos": list(execucao.arquivos_exigidos),
    }


def depurar(execucao, raiz, tipo, **dados):
    if not execucao.depurar:
        return

    execucao.seq_debug += 1
    linha = {
        "seq": execucao.seq_debug,
        "hora": datetime.now().isoformat(),
        "estado": execucao.estado,
        "tipo": tipo,
        **dados,
    }
    with open(Path(raiz) / ".minicode" / "debug.jsonl", "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")

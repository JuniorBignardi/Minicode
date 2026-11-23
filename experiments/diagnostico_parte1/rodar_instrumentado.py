"""Roda um conjunto de benchmark com o agente atual e guarda tudo o que a análise de falhas precisa.

Uso:  python experiments/diagnostico_parte1/rodar_instrumentado.py <facil|dificil> <pasta_destino> [repeticoes] [id ...]

Para cada execução, em <pasta_destino>/<conjunto>_r<N>/tarefa_NN/:
  .minicode/                      o rastro do agente
  .minicode/chamadas_llm.jsonl    cada chamada à LLM (fase, mensagens, resposta, tempo): matéria-prima do dataset
  .minicode/snapshots/diag_NN/    uma cópia do projeto no momento de cada diagnóstico
  resultado.json                  estado final, métricas, plano de testes e se o código final está correto
Execuções que já têm resultado.json são puladas, então dá para retomar depois de uma interrupção.
Variáveis de ambiente: as do MiniCode (MINICODE_API_BASE, MINICODE_API_KEY, MINICODE_MODEL).
"""
import contextlib
import copy
import json
import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))   # experiments/ (oraculo)
sys.path.insert(0, str(AQUI.parents[1] / "eval_tasks"))

# --- configuração ---
PAUSA = float(os.environ.get("PAUSA_ENTRE_CHAMADAS", "0"))   # segundos de espera antes de cada chamada (0 = sem pausa)
NAO_COPIAR = shutil.ignore_patterns(".minicode", ".git", "__pycache__", ".pytest_cache")   # fora dos snapshots
TEMPERATURA_DAS_FASES_SEM_SCHEMA = {0.6: "spec", 0.5: "plano"}   # TEMPERATURA_POR_FASE em agent/conversas/fases.py


def fase_da_chamada(temperatura, argumentos):
    # as revisões e o diagnóstico têm schema com nome; a spec e o plano se distinguem pela temperatura
    formato = argumentos.get("response_format")
    if formato:
        return formato["json_schema"]["name"]
    return TEMPERATURA_DAS_FASES_SEM_SCHEMA.get(temperatura, "outra")


def criar_chat(chat_real, raiz):
    # devolve uma função chat que se comporta como a original, mas grava cada chamada no registro
    registro = raiz / ".minicode" / "chamadas_llm.jsonl"
    registro.parent.mkdir(parents=True, exist_ok=True)
    diagnosticos = [0]   # contador dentro de uma lista, para a função interna poder alterá-lo

    def chat(mensagens, temperature=0, **argumentos):
        if PAUSA:
            time.sleep(PAUSA)
        fase = fase_da_chamada(temperature, argumentos)
        pedido = copy.deepcopy(mensagens)   # o agente acrescenta a resposta à mesma lista depois da chamada

        # a cada diagnóstico, guarda uma cópia do projeto naquele momento (usada depois pelo oráculo)
        if fase == "diagnostico":
            diagnosticos[0] += 1
            shutil.copytree(raiz, registro.parent / "snapshots" / f"diag_{diagnosticos[0]:02d}", ignore=NAO_COPIAR)

        inicio = time.time()
        resposta, erro = None, None
        try:
            resposta = chat_real(mensagens, temperature=temperature, **argumentos)
            return resposta
        except Exception as e:
            erro = f"{type(e).__name__}: {e}"
            raise
        finally:
            # grava a chamada mesmo quando ela falhou (o erro fica no registro)
            with open(registro, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "fase": fase, "temperatura": temperature, "mensagens": pedido, "resposta": resposta,
                    "erro": erro, "segundos": round(time.time() - inicio, 2),
                }, ensure_ascii=False) + "\n")
    return chat


def rodar_uma(tarefa, raiz, chat_real, rodar_agente):
    # começa de uma pasta limpa, só com os arquivos iniciais da tarefa
    shutil.rmtree(raiz, ignore_errors=True)
    raiz.mkdir(parents=True)
    for caminho, conteudo in tarefa["arquivos"].items():
        (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
        (raiz / caminho).write_text(conteudo, encoding="utf-8")

    # roda o agente, com a tela desviada para saida.log
    inicio, erro, execucao = time.time(), None, None
    with open(raiz / "saida.log", "w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
        try:
            execucao = rodar_agente(tarefa["tarefa"], raiz, criar_chat(chat_real, raiz))
        except Exception as e:
            erro = f"{type(e).__name__}: {e}"

    try:
        codigo_correto = bool(tarefa["verificar"](raiz))   # vale mesmo se o agente terminou em FAILED
    except Exception:
        codigo_correto = False

    # se o agente falhou antes de terminar (execucao vazia), os campos ficam com valores neutros
    resultado = {
        "id": tarefa["id"], "nome": tarefa["nome"], "tipo": tarefa["tipo"], "erro_do_corredor": erro,
        "estado": execucao.estado if execucao else "ERRO", "codigo_correto": codigo_correto,
        "reparos": execucao.tentativas if execucao else 0,
        "chamadas": execucao.chamadas_llm if execucao else 0,
        "iteracoes": execucao.iteracoes if execucao else 0,
        "segundos": round(time.time() - inicio),
        "arquivos_alterados": list(execucao.arquivos_alterados) if execucao else [],
        "plano_de_testes": execucao.plano_de_testes if execucao else None,
        "testes_descartados": (
            [list(t) if isinstance(t, tuple) else t for t in execucao.testes_descartados] if execucao else []
        ),
    }
    (raiz / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")
    return resultado


def main():
    conjunto, destino = sys.argv[1], Path(sys.argv[2])
    repeticoes = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ids = {int(x) for x in sys.argv[4:]}   # sem ids, roda todas as tarefas do conjunto

    from minicode.agent.orquestrador import rodar_agente
    from minicode.llm.client import chat as chat_real
    import tarefas_dificeis
    import tarefas_faceis
    tarefas = (tarefas_faceis if conjunto == "facil" else tarefas_dificeis).TAREFAS

    for rodada in range(1, repeticoes + 1):
        for tarefa in tarefas:
            if ids and tarefa["id"] not in ids:
                continue
            raiz = destino / f"{conjunto}_r{rodada}" / f"tarefa_{tarefa['id']:02d}"
            if (raiz / "resultado.json").exists():
                continue   # já rodou: permite retomar depois de uma interrupção
            r = rodar_uma(tarefa, raiz, chat_real, rodar_agente)
            print(
                f"[r{rodada} {tarefa['id']:02d}] {tarefa['nome']:34} -> {r['estado']:6} correto={r['codigo_correto']} "
                f"reparos={r['reparos']} chamadas={r['chamadas']} {r['segundos']}s",
                flush=True,
            )


if __name__ == "__main__":
    main()

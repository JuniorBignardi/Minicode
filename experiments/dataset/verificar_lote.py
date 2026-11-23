"""Verificação em lote dos exercícios novos: segundo solucionador + juiz (pedido vs. referência) + similaridade.

Uso: python experiments/dataset/verificar_lote.py <entrada.jsonl> <saida.json> [threads]
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(RAIZ / "src"))
import gerar_v3

# O segundo solucionador é o modelo maior (ULTRA); o juiz é o menor (SUPER)
SUPER, ULTRA = "nvidia/nemotron-3.5-super-vl-120b-a12b", "nvidia/nemotron-3-ultra-550b-a55b"
JUIZ = """Você revisa exercícios de programação. Recebe o PEDIDO (o que o programador lê), a SPEC, a REFERÊNCIA (código correto) e os CASOS (entrada e valor esperado, obtidos executando a referência).
Procure apenas problemas reais que fariam um programador competente, lendo só o pedido e a spec, errar algum caso. Exemplos: comportamento da referência que o pedido contradiz ou não define (exceção não citada, divisão por zero, ordem do resultado, tratamento de espaços/maiúsculas, nome de método/atributo/chave, valor de constante ou tabela, desempate, tipo de retorno), critério da spec sem relação com o pedido, caso que testa algo que o pedido não define.
Ignore detalhes de estilo. Se não houver problema, devolva lista vazia.
Responda SOMENTE com JSON: {"problemas": [{"caso": <índice do caso começando em 0 ou -1 se geral>, "motivo": "<uma frase>"}]}"""


# Pede ao juiz que leia o exercício e aponte problemas reais (pedido ambíguo, referência que contradiz o pedido etc.).
# Se a chamada ou a leitura do JSON falhar, devolve um "problema" -2 em vez de quebrar o lote.
def julgar(juiz, r):
    casos = "\n".join(f"{i}: {c['entrada']}  =>  {c['esperado']}" for i, c in enumerate(r["casos"]))
    texto = (
        f"PEDIDO:\n{r['pedido']}\n\nSPEC:\n{r['especificacao']}\n\n"
        f"REFERÊNCIA:\n{r['referencia']}\n\nCASOS:\n{casos}"
    )
    try:
        saida = juiz(
            [{"role": "system", "content": JUIZ}, {"role": "user", "content": texto}],
            temperature=0.0,
            max_tokens=2500,
        )
        return json.loads(re.search(r"\{.*\}", saida, re.S).group(0))["problemas"]
    except Exception as erro:
        return [{"caso": -2, "motivo": f"juiz falhou: {type(erro).__name__}"}]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from professor import Professor

    entrada, saida = Path(sys.argv[1]), Path(sys.argv[2])
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    registros = [json.loads(l) for l in entrada.read_text(encoding="utf-8").splitlines() if l.strip()]

    # os dois modelos gravam o consumo de tokens no mesmo arquivo
    uso = RAIZ / "experiments" / "execucoes" / "uso_tokens.jsonl"
    solucionador = Professor(ULTRA, por_minuto=30, tempo=90, arquivo_de_uso=uso)
    juiz = Professor(SUPER, por_minuto=30, tempo=90, arquivo_de_uso=uso)

    # cada exercício passa pelo segundo solucionador (resolve só pelo pedido e a spec) e pelo juiz
    def verificar(r):
        return {
            "id": r["id"],
            "nome": r["nome"],
            "solucionador": gerar_v3.segundo_solucionador(solucionador, r),
            "juiz": julgar(juiz, r),
        }

    resultados = []
    with ThreadPoolExecutor(threads) as pool:
        for i, res in enumerate(pool.map(verificar, registros), 1):
            resultados.append(res)
            if i % 10 == 0:
                print(f"  {i}/{len(registros)}", flush=True)
    saida.write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")

    # resumo: quantos exercícios em cada situação do solucionador e quantos o juiz marcou
    sit = {}
    for x in resultados:
        sit[x["solucionador"]["situacao"]] = sit.get(x["solucionador"]["situacao"], 0) + 1
    print(
        "solucionador:", sit, "| com problema do juiz:", sum(1 for x in resultados if x["juiz"]),
        flush=True,
    )


if __name__ == "__main__":
    main()

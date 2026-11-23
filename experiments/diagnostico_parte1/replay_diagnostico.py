"""Reenvia ao modelo os diagnósticos reais já gravados, com variações do prompt, e compara com o oráculo.

Separa duas hipóteses: o 14B não sabe diagnosticar (nenhum prompt ajuda) ou o nosso prompt é que atrapalha
(uma variação melhora). Usa os prompts exatos gravados por rodar_instrumentado.py.

Uso:  python experiments/diagnostico_parte1/replay_diagnostico.py <pasta_dos_resultados> [pasta_de_saida]
Precisa das variáveis MINICODE_API_BASE, MINICODE_API_KEY e MINICODE_MODEL.
"""
import copy
import json
import sys
import time
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent

TEXTO_TAXA_DE_BASE = (
    "\n\nAtenção: neste projeto os testes foram escritos por uma LLM, que erra valores esperados com frequência. "
    "Na grande maioria das falhas o erro está no TESTE (valor esperado errado, entrada que viola várias regras de uma vez), "
    "e não no código. Antes de culpar o código, confirme que o valor esperado do teste está de acordo com a especificação."
)
TEXTO_DERIVAR = (
    "\n\nMétodo obrigatório: em 'evidencias', escreva primeiro (a) o valor que a ESPECIFICAÇÃO exige para a entrada do teste "
    "que falhou, calculado só a partir da especificação, SEM olhar o código; (b) o valor que o TESTE espera; (c) o valor que o "
    "CÓDIGO devolve. Se (a) for diferente de (b), a classificação é TEST_BUG. Se (a) for igual a (b) e diferente de (c), é CODE_BUG."
)

# O schema do agente obriga a classificação a vir PRIMEIRO: o modelo decide antes de raciocinar.
# As variações "evidencias_primeiro" pedem o raciocínio antes do veredito.
ORDEM_DO_AGENTE = ["classificacao", "citacao_da_spec", "evidencias", "proxima_acao"]
ORDEM_RACIOCINIO_PRIMEIRO = ["evidencias", "citacao_da_spec", "classificacao", "proxima_acao"]

VARIACOES = {   # nome -> (texto acrescentado ao prompt de sistema, ordem dos campos do schema)
    "controle": ("", ORDEM_DO_AGENTE),
    "taxa_de_base": (TEXTO_TAXA_DE_BASE, ORDEM_DO_AGENTE),
    "derivar_antes": (TEXTO_DERIVAR, ORDEM_DO_AGENTE),
    "evidencias_primeiro": ("", ORDEM_RACIOCINIO_PRIMEIRO),
    "evidencias_primeiro_taxa_de_base": (TEXTO_TAXA_DE_BASE, ORDEM_RACIOCINIO_PRIMEIRO),
    "evidencias_primeiro_derivar": (TEXTO_DERIVAR, ORDEM_RACIOCINIO_PRIMEIRO),
}


def lado(classificacao):
    return {"CODE_BUG": "CODE_BUG", "TEST_BUG": "TEST_BUG", "PLAN_BUG": "TEST_BUG"}.get(classificacao, "indeterminado")


def casos_gravados(pasta):
    # (identificação, mensagens do diagnóstico, veredito do oráculo) de cada diagnóstico que o oráculo consegue julgar
    casos = []
    for linha in json.loads((pasta / "diagnostico_falhas.json").read_text(encoding="utf-8")):
        tarefa = pasta / linha["rodada"] / f"tarefa_{linha['id']:02d}"
        registro = tarefa / ".minicode" / "chamadas_llm.jsonl"
        if not registro.is_file():
            continue
        chamadas = [json.loads(x) for x in registro.read_text(encoding="utf-8").splitlines() if x.strip()]
        chamadas = [c for c in chamadas if c["fase"] == "diagnostico"]
        if len(chamadas) != len(linha["diagnosticos"]):
            continue   # diagnóstico inconclusivo no meio: a correspondência não é segura
        for numero, (chamada, diag) in enumerate(zip(chamadas, linha["diagnosticos"]), start=1):
            if diag["oraculo"] in ("CODE_BUG", "TEST_BUG"):
                casos.append((f"{linha['rodada']}/{linha['nome']}#{numero}", chamada["mensagens"], diag["oraculo"], diag["classificacao"]))
    return casos


def main():
    pasta = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else pasta
    from minicode.llm.client import chat
    from minicode.llm.esquema import formato_da_resposta
    from minicode.spec.diagnostico import ESQUEMA_DIAGNOSTICO, interpretar_diagnostico

    casos = casos_gravados(pasta)
    print(len(casos), "diagnósticos com veredito do oráculo", flush=True)

    escolhidas = sys.argv[3:] or list(VARIACOES)
    arquivo = saida / "replay_diagnostico.json"
    anteriores = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.is_file() else []
    resultados = [r for r in anteriores if r["variacao"] not in escolhidas]   # refazer uma variação substitui a anterior
    for nome in escolhidas:
        extra, ordem = VARIACOES[nome]
        esquema = {**ESQUEMA_DIAGNOSTICO, "properties": {campo: ESQUEMA_DIAGNOSTICO["properties"][campo] for campo in ordem}}
        formato = formato_da_resposta(esquema, "diagnostico")
        for identificacao, mensagens, oraculo, original in casos:
            pedido = copy.deepcopy(mensagens)
            pedido[0]["content"] += extra
            resposta = None
            for _ in range(2):
                try:
                    resposta = chat(pedido, temperature=0.2, response_format=formato)
                    break
                except Exception:
                    time.sleep(3)
            diagnostico = interpretar_diagnostico(resposta) if resposta else None
            resultados.append({"variacao": nome, "caso": identificacao, "oraculo": oraculo,
                               "modelo": lado(diagnostico["classificacao"]) if diagnostico else "sem_resposta",
                               "classificacao": diagnostico["classificacao"] if diagnostico else None, "original": original})
        parcial = [r for r in resultados if r["variacao"] == nome]
        print(f"{nome}: acurácia {sum(r['modelo'] == r['oraculo'] for r in parcial)}/{len(parcial)}", flush=True)
        arquivo.write_text(json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n| Variação | Acurácia | Recall TEST_BUG | Recall CODE_BUG | Disse CODE_BUG quando o teste estava errado |\n|---|---|---|---|---|")
    for nome in dict.fromkeys(r["variacao"] for r in resultados):
        r = [x for x in resultados if x["variacao"] == nome]
        teste = [x for x in r if x["oraculo"] == "TEST_BUG"]
        codigo = [x for x in r if x["oraculo"] == "CODE_BUG"]
        print(f"| {nome} | {sum(x['modelo'] == x['oraculo'] for x in r)}/{len(r)} | "
              f"{sum(x['modelo'] == 'TEST_BUG' for x in teste)}/{len(teste)} | {sum(x['modelo'] == 'CODE_BUG' for x in codigo)}/{len(codigo)} | "
              f"{sum(x['modelo'] == 'CODE_BUG' for x in teste)}/{len(teste)} |")


if __name__ == "__main__":
    main()

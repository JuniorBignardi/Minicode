# Experimentos da Parte 2

Tudo o que gera o dataset, treina a avaliação e mede os modelos. O treino em si está em [`notebooks/`](../notebooks/), o dataset em [`datasets/plano_de_testes/`](../datasets/plano_de_testes/) e a hipótese em [`docs/hipotese_parte2.md`](../docs/hipotese_parte2.md).

## O que cada pasta tem

| Caminho | Para quê |
|---|---|
| `oraculo.py`, `referencias_faceis.py`, `referencias_dificeis.py`, `validar_referencias.py` | **O oráculo.** Executa cada caso de teste na solução de referência da tarefa e diz se o valor esperado está certo, errado ou não é avaliável. As referências das 25 tarefas foram validadas contra os verificadores ocultos da Parte 1 |
| `avaliar_nivel1.py`, `avaliar_endpoint.py`, `avaliar_resultado_colab.py` | **Nível 1** (a função sozinha): mandam os prompts a um modelo e pontuam os planos de testes com o oráculo |
| `analise_nivel1.py`, `auditar_inavaliaveis.py` | Análise estatística pareada (bootstrap por tarefa) e auditoria manual dos casos "inavaliáveis" |
| `nivel2.py` | **Nível 2** (o agente completo): roda o MiniCode nas 25 tarefas nas configurações A, B e C e resume o TaskSuccessRate |
| `dataset/` | O pipeline que gerou o dataset: professores, filtros, montagem, segundo solucionador e auditoria (ver abaixo). `montar_dataset.py` montou os 687 exemplos originais; `gerar_v3.py` gerou os 67 do Qwen cloud |
| `diagnostico_parte1/` | A análise dos erros do Qwen-14B na Parte 1, que motivou a hipótese (os 38% de valores esperados errados) |
| `resultados/` | **Os resultados versionados** (ver [`resultados/README.md`](resultados/README.md)) |
| `execucoes/` | Saídas brutas e intermediárias (logs, pilotos, versões antigas do dataset). **Não vai para o git** |

## Como reproduzir

Pré-requisitos: `pip install -e ".[dev]"` na raiz, e um endpoint compatível com a API da OpenAI para o modelo avaliado (Ollama ou vLLM). Nenhuma chave vai no repositório.

**Nível 1: um modelo, as 140 entradas (60 reais e 80 sintéticas), com JSON Schema e temperatura 0,3**
```
python experiments/avaliar_endpoint.py <url_base>/v1 <modelo> <nome> --schema
python experiments/avaliar_endpoint.py <url_base>/v1 <modelo> <nome> --schema --exemplos 2     # com 2 exemplos do treino no prompt
python experiments/analise_nivel1.py experiments/resultados/nivel1                              # comparações pareadas e sensibilidade
```
O script grava, em `experiments/execucoes/nivel1/`, a chamada completa (prompt, parâmetros, resposta, tokens), a nota de cada caso e o resumo. Se cair no meio, rodar de novo continua de onde parou. Sem os logs da Parte 1, os 60 prompts reais vêm de `datasets/plano_de_testes/entradas_reais.json`.

**Nível 2: o agente completo**
```
# o 14B (como na Parte 1) e, para a configuração B, o modelo especializado:
export MINICODE_API_BASE=<url do 14B>/v1 MINICODE_API_KEY=ollama MINICODE_MODEL=qwen2.5:14b
export MINICODE_PLAN_API_BASE=<url do 1,5B>/v1 MINICODE_PLAN_MODEL=<nome do adaptador>
python experiments/nivel2.py rodar experiments/execucoes/nivel2 --repeticoes 1 --paralelo 3
python experiments/nivel2.py resumo experiments/execucoes/nivel2
```
Configurações: **A** = Qwen-14B sozinho; **B** = o 1,5B ajustado escreve a primeira versão do plano de testes e o 14B faz o resto; **C** = sem a etapa do plano de testes (ablação). A ablação também pode ser pedida diretamente com `MINICODE_ABLACAO="planejar_testes=False"`.

**Dataset**
```
python experiments/dataset/gerar_v3.py <modelo_gerador|qwen> <modelo_solucionador> <saida.jsonl> <quantidade> [semente] [threads]
python experiments/dataset/verificar_lote.py <exercicios.jsonl> <saida.json>        # segundo solucionador e juiz
python experiments/dataset/auditar_dataset.py <pasta_do_dataset>                    # estrutura, duplicatas, contaminação, reexecução
python experiments/dataset/montar_dataset.py <pasta_de_saida> <exercicios.jsonl> ...  # junta os lotes e monta treino, validação e teste
```
A geração exige as chaves dos provedores (variáveis `MINICODE_API_*`, `ENDPOINT_PROF*`, `QWEN_*`, em `.env`). O dataset final já está pronto em `datasets/plano_de_testes/`, então reproduzir a geração não é necessário para treinar nem avaliar.

## Onde está cada resultado do relatório

| Pergunta | Arquivo |
|---|---|
| Acerto de cada modelo (base, base com 2 exemplos, ajustado, 14B) | `resultados/nivel1/*_resumo.json` e `resultados/nivel1/analise.md` |
| Cada caso de cada plano, com a nota do oráculo | `resultados/nivel1/*_avaliacao.jsonl` |
| Prompt e resposta completos de cada chamada | `resultados/nivel1/*_respostas.jsonl` |
| Auditoria manual dos 355 casos inavaliáveis | `resultados/nivel1/auditoria_inavaliaveis/` |
| Curvas de perda do treino | `resultados/treino/` |
| Agente completo (A, B e C) | `resultados/nivel2/` |

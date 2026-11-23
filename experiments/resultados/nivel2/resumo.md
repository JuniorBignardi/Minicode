# Nível 2: agente completo (25 tarefas)

| configuração | execuções | TaskSuccessRate (IC 95%) | por repetição | FirstAttempt | iterações | chamadas ao LLM | s/tarefa | erros de infraestrutura | usou o especialista |
|---|---|---|---|---|---|---|---|---|---|
| A: 14B sozinho | 25 (+0 com erro de infra) | **88.0%** (72 a 100) | 88% | 64% | 17.6 | 17.6 | 186 | 0 | - |
| B: 14B + 1,5B ajustado no plano de testes | 25 (+0 com erro de infra) | **72.0%** (52 a 88) | 72% | 44% | 23.4 | 23.4 | 269 | 0 | 25/25 |
| C: sem plano de testes (ablação) | 25 (+0 com erro de infra) | **84.0%** (68 a 96) | 84% | 64% | 14.9 | 14.9 | 140 | 0 | - |

## Diferenças em relação ao A (pareadas por tarefa; bootstrap sobre as 25 tarefas)

| comparação | diferença em pontos (IC 95%) | leitura |
|---|---|---|
| B − A | -16.0 (-32 a -4) | intervalo não contém 0 |
| C − A | -4.0 (-16 a +8) | intervalo contém 0: não dá para afirmar diferença |

## Por tipo de tarefa (corretas / execuções válidas)

| tipo | A | B | C |
|---|---|---|---|
| api | 2/2 | 2/2 | 2/2 |
| arquivos | 0/1 | 0/1 | 0/1 |
| bug | 3/3 | 3/3 | 3/3 |
| bug em classe | 1/1 | 1/1 | 1/1 |
| bug sutil | 1/1 | 0/1 | 1/1 |
| classe com estado | 1/1 | 1/1 | 1/1 |
| criar testes | 2/2 | 0/2 | 1/2 |
| implementar | 4/4 | 3/4 | 4/4 |
| modificar API | 1/1 | 1/1 | 1/1 |
| refatorar | 3/3 | 3/3 | 3/3 |
| texto | 0/1 | 0/1 | 1/1 |
| usa codigo existente | 1/1 | 1/1 | 0/1 |
| validacao | 2/3 | 2/3 | 2/3 |
| varios arquivos | 1/1 | 1/1 | 1/1 |

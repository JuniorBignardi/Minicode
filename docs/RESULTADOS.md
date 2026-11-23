# Resultados da Parte 2

*Gerado por `experiments/gerar_resultados_md.py` a partir de `experiments/resultados/`. Detalhes e análises extras: [`RESULTADOS_DETALHADO.md`](RESULTADOS_DETALHADO.md).*

## A pergunta
Dá para treinar um modelo **pequeno** (Qwen 1,5B, com LoRA) para fazer **uma etapa** do agente, escrever o plano de testes, tão bem quanto um modelo **grande** (Qwen 14B)? E isso melhora o agente?

## Função isolada (Nível 1): Accuracy dos testes que o modelo escreve
O modelo escreve casos de teste (uma chamada e o valor esperado). Um programa executa cada chamada no código correto da tarefa e confere. **Accuracy = casos certos ÷ casos avaliados.** Prova: 60 pedidos das 25 tarefas da Parte 1, que o modelo nunca viu no treino.

| Modelo | **Accuracy** | IC 95% |
|---|---|---|
| 1,5B base (sem treino) | **10%** | 0% a 25% |
| 1,5B base com 2 exemplos no prompt | **32%** | 18% a 47% |
| **1,5B treinado com LoRA** | **65%** | 55% a 76% |
| Qwen-14B (modelo grande) | **67%** | 51% a 82% |

- Treinar elevou a Accuracy em **55 pontos** sobre o modelo sem treino (margem +39 a +69). Isso é firme.
- Contra o 14B o 1,5B fica **2 pontos abaixo**, e a margem (-16 a +11) inclui zero. Conclusão: **no mesmo nível**, não melhor.

## O agente completo: as mesmas métricas da Parte 1 (25 tarefas, teste oculto decide)
| Configuração | **TaskSuccessRate** | **FirstAttemptSuccess** | **AverageIterations** | **AverageLLMCalls** |
|---|---|---|---|---|
| A: Qwen-14B sozinho | **22/25 = 88%** | 64% | 17,6 | 17,6 |
| B: 1,5B treinado escreve o plano de testes + 14B | **18/25 = 72%** | 44% | 23,4 | 23,4 |
| C: sem plano de testes (ablação) | **21/25 = 84%** | 64% | 14,9 | 14,9 |

O treinado **não ajudou** o agente: B ficou abaixo de A, e o agente sem plano de testes (C) quase empatou com A. **A melhora na função isolada não virou melhora no agente.**

## Em que confiar
- **Firme:** a Accuracy acima. É calculado por código, sem opinião de pessoa nem de outro modelo, e as soluções corretas passam nos testes ocultos da Parte 1.
- **Cuidado:** o agente completo tem só 25 tarefas e uma execução por configuração. Mostra que **não houve ganho**, mas não prova que o treinado atrapalha.
- **Fora desta página:** auditorias manuais e outras formas de medir estão no anexo. Elas mantêm a conclusão de "mesmo nível", com uma ressalva: contando só os planos em que **todos** os casos estão certos, o 14B vai melhor (33% contra 20%).

## O que NÃO dá para afirmar
- Que o 1,5B é melhor que o 14B (só empata).
- Que o resultado vale para outras tarefas além dessas 25.

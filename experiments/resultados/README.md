# Resultados da Parte 2

Tudo aqui é saída gerada pelos scripts de `experiments/`, copiada de `experiments/execucoes/` (que o git ignora) para ficar versionada.

| Pasta | Conteúdo |
|---|---|
| `nivel1/` | O Nível 1 (a função sozinha) para 5 modelos: 14B, 1,5B base, 1,5B base com 2 exemplos, 1,5B ajustado (3 épocas) e 1,5B ajustado (melhor ponto). Todos com o mesmo prompt, JSON Schema e temperatura 0,3, nas mesmas 140 entradas (60 reais e 80 sintéticas). Cada modelo tem `*_respostas.jsonl` (prompt e resposta completos), `*_avaliacao.jsonl` (nota de cada caso) e `*_resumo.json`. `analise.md` traz as comparações pareadas |
| `nivel1/auditoria_inavaliaveis/` | Leitura manual dos 355 casos que o oráculo não conseguiu julgar (14B, ajustado de 3 épocas e base): o veredito de cada um e o resumo |
| `treino/` | O histórico de perdas (treino e validação) e as curvas dos dois treinos: `treino1` (3 épocas) e `treino2` (com adaptador por época e retorno ao melhor ponto da validação) |
| `nivel2/` | O agente completo nas 25 tarefas, nas configurações A, B e C |

Os pesos do modelo (adaptadores LoRA, ~70 MB cada) não estão no repositório, como o enunciado permite: estão [nesta pasta do Google Drive](https://drive.google.com/drive/folders/1N4rfJPWTsBHQek1-lflZ8nffpZXw1j9H?usp=sharing).

# Qualidade do plano de testes que o agente usou × resultado da tarefa

O plano final gravado pelo agente (`test_plan.md`) pontuado pelo oráculo. "Plano com erro" = pelo menos um caso com valor esperado errado.

| configuração | execuções | valores corretos no plano | planos sem nenhum erro | tarefas corretas com plano SEM erro | tarefas corretas com plano COM erro |
|---|---|---|---|---|---|
| A | 25 | 77.9% (60/77) | 16/25 | 15/16 | 7/9 |
| B | 25 | 64.6% (73/113) | 8/25 | 5/8 | 13/17 |

## Execuções com plano com erro

| config | tarefa | plano: certos/errados | tarefa correta | reparos |
|---|---|---|---|---|
| A | dificil 01 remover usuario (repo + servico) | 1/2 | sim | 0 |
| A | dificil 05 perimetro | 1/1 | sim | 1 |
| A | dificil 08 validar_senha | 4/2 | **não** | 3 |
| A | dificil 10 ler_csv | 0/3 | **não** | 0 |
| A | facil 01 fatorial | 1/2 | sim | 0 |
| A | facil 04 contar palavras | 2/4 | sim | 3 |
| A | facil 05 media | 0/1 | sim | 0 |
| A | facil 09 desconto | 2/1 | sim | 0 |
| A | facil 14 area reutiliza | 0/1 | sim | 2 |
| B | dificil 01 remover usuario (repo + servico) | 2/1 | sim | 3 |
| B | dificil 02 mesclar intervalos | 2/3 | **não** | 3 |
| B | dificil 03 carrinho | 3/2 | sim | 3 |
| B | dificil 05 perimetro | 3/2 | sim | 1 |
| B | dificil 06 arredondar_moeda | 3/2 | sim | 0 |
| B | dificil 07 filtros em listar | 3/3 | sim | 0 |
| B | dificil 08 validar_senha | 1/10 | **não** | 3 |
| B | dificil 09 pilha | 3/1 | sim | 1 |
| B | facil 01 fatorial | 5/1 | sim | 2 |
| B | facil 02 palindromo | 3/2 | **não** | 3 |
| B | facil 04 contar palavras | 1/3 | sim | 3 |
| B | facil 05 media | 2/2 | sim | 1 |
| B | facil 06 maior de negativos | 3/1 | sim | 0 |
| B | facil 09 desconto | 3/1 | sim | 0 |
| B | facil 10 testes de estoque | 0/4 | **não** | 3 |
| B | facil 14 area reutiliza | 2/1 | sim | 0 |
| B | facil 15 list comprehension | 2/1 | sim | 0 |

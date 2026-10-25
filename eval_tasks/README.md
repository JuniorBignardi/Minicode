# Avaliação do MiniCode

Duas baterias de tarefas pequenas, cada uma com um **verificador oculto**: um arquivo de testes que o agente nunca vê. O sucesso é decidido por esses testes (`pytest`), e não pela opinião do agente nem pelos testes que ele mesmo escreveu.

| Arquivo | Tarefas | Papel |
|---|---|---|
| `rodar_facil.py` | 15 | conjunto fácil: função, bug, API, criação de testes, validação, refatoração |
| `rodar_dificil.py` | 10 | conjunto difícil: vários arquivos, bug sutil, classe com estado, arquivos, uso de código existente, API, validação, refatoração |

## Tarefas

**Fácil:** fatorial, palíndromo, fibonacci, contar palavras · média, maior de negativos, `eh_par` invertido · saudação formal, desconto · testes de estoque, testes de primo · `criar_usuario`, `validar_email` · área reutiliza, list comprehension.

**Difícil:** remover usuário (repositório + serviço), mesclar intervalos, carrinho, contar linhas e palavras, perímetro (usa `distancia` existente), `arredondar_moeda`, filtros em `listar`, `validar_senha`, pilha, `ler_csv`.

Os tipos cobrem os que o enunciado pede (§14): implementação de função, correção de bug, modificação de API, criação de testes, validação de dados e pequena refatoração.

## Como cada tarefa é avaliada

1. O executor cria uma pasta limpa para a tarefa e grava nela os arquivos iniciais (alguns projetos já trazem código e um `tests/test_original.py`, que o agente não pode alterar).
2. Roda `rodar_agente` com o pedido em linguagem natural.
3. Se o agente terminou em `DONE`, copia o verificador oculto (`test_oculto.py`) para a pasta e roda `pytest`. A tarefa só conta como **correta** se esse arquivo passa.
   - Tarefas de refatoração também conferem a estrutura do código (ex.: a função auxiliar existe e `round(` só aparece nela).
   - Tarefas de "criar testes" conferem que o agente criou ao menos N funções `test_` novas.
4. Cada tarefa grava o rastro completo em `<saida>/tarefa_NN/.minicode/`.

## Métricas

| Métrica | Definição |
|---|---|
| **TaskSuccessRate** | tarefas corretas no verificador oculto ÷ total |
| **FirstAttemptSuccess** | tarefas corretas **sem nenhum reparo** ÷ total |
| **AverageIterations** | média de iterações do laço (cada chamada à LLM é uma iteração) |
| **AverageLLMCalls** | média de chamadas à LLM por tarefa |

Também é impresso o resumo por tipo de tarefa e os eventos de harness por tarefa (`escrita_protegida`, `finish_recusado`, `limite_de_leituras` etc.).

## Como rodar

Com o ambiente configurado (veja o README principal):

```bash
export MINICODE_API_BASE=...  MINICODE_API_KEY=...  MINICODE_MODEL=...

python eval_tasks/rodar_facil.py   /caminho/da/saida
python eval_tasks/rodar_dificil.py /caminho/da/saida
python eval_tasks/rodar_dificil.py /caminho/da/saida 3 5     # só as tarefas 3 e 5
```

O executor espera 1 s entre chamadas (o endpoint é compartilhado). Um conjunto difícil leva de 10 a 15 minutos.

## Cuidados com a interpretação

- **Ruído:** duas execuções idênticas diferem em cerca de ±20 pontos de taxa de sucesso (o modelo é estocástico e são só 10 tarefas). Diferença de uma ou duas tarefas entre configurações não é evidência.
- **Contaminação:** as 10 tarefas difíceis foram usadas durante o desenvolvimento para achar falhas do agente. A taxa nelas é otimista; o enunciado (§15) avalia também em tarefas inéditas.
- **Verificadores validados:** cada verificador oculto foi conferido contra uma solução de referência correta (ele deve passar nela), para evitar falsos negativos que punissem o agente por erro do próprio verificador (isso já aconteceu uma vez, com uma expressão regular mal escapada).

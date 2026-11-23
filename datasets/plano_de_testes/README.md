# Dataset do plano de testes

Dataset usado para especializar uma LLM pequena (Qwen2.5-1.5B-Instruct, com LoRA) na função **gerar o plano de testes** do MiniCode. A hipótese e os critérios de avaliação estão em [`docs/hipotese_parte2.md`](../../docs/hipotese_parte2.md).

## O que é cada exemplo

- **Entrada:** o prompt que o agente envia na etapa do plano de testes: o pedido do usuário, a especificação (com os critérios de aceitação) e o plano de implementação. É exatamente o que `minicode.spec.plano_de_testes.mensagens_plano_de_testes` produz; o prompt de sistema é o mesmo em todos os exemplos.
- **Saída:** um JSON `{"casos": [{"criterio", "entrada", "esperado"}]}`, com pelo menos um caso por critério. `entrada` é uma expressão Python executável e `esperado` é o valor (ou a exceção) que ela produz.
- O `esperado` **vem da execução da solução de referência pelo nosso programa, nunca de um modelo**. Esse é o ponto central do dataset.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `exemplos_treino.jsonl`, `exemplos_validacao.jsonl`, `exemplos_teste.jsonl` | o formato de treino: `tarefa_id`, `modelo` (quem escreveu o exercício), `mensagens` (system e user) e `resposta` |
| `registros_*.jsonl` | a fonte de cada exemplo: `pedido`, `especificacao`, `plano`, `referencia` (a solução correta), `entradas`, `casos`, `tema`, `estilo`, `arquivo`, `nome` |
| `entradas_reais.json` | os 60 prompts reais que o agente mandou ao Qwen-14B nas 25 tarefas do benchmark (usados só na avaliação, nunca no treino) |

## Tamanho e divisão

| Conjunto | Exemplos | Do Qwen cloud (`q*`) |
|---|---|---|
| treino | 754 | 67 |
| validação | 79 | 9 |
| teste | 80 | 9 |

A divisão é **por exercício** (nenhum exercício aparece em dois conjuntos). Nos exercícios do Qwen cloud, o sorteio foi por **tema**, para que exercícios parecidos fiquem no mesmo conjunto. O teste não foi usado no treino nem na escolha de hiperparâmetros (a escolha do melhor ponto do treino usa só a validação).

## Como foi gerado

1. **Professores:** modelos grandes escrevem um exercício completo por chamada (pedido, solução de referência, spec sem resultados, plano e **apenas as entradas** dos casos). Foram usados Nemotron 3 Ultra 550B e Nemotron 3.5 Super 120B (API da NVIDIA) e DeepSeek v4.1 Flash (Qwen cloud). Os ids `e*` vêm dos Nemotron e os `q*` do Qwen cloud.
2. **Temas:** cada chamada recebe um tema sorteado (sem reposição entre lotes), um estilo e o número de regras, para variar o conteúdo.
3. **Valores esperados:** o programa executa as entradas na referência (duas vezes, para descartar não determinismo) e grava o resultado como `esperado`.
4. **Filtros automáticos:** código que não executa; resultado não determinístico; saídas pouco variadas; exercícios parecidos com as 25 tarefas do benchmark; nomes de função ou arquivo repetidos; critérios sobre a implementação em vez do comportamento; texto em inglês; atributos privados nos casos; métodos ou valores usados nos casos que o pedido não menciona.
5. **Segundo solucionador:** outro modelo resolve o exercício só pelo pedido e pela spec, e o código dele roda nas mesmas entradas; divergências são conferidas à mão.
6. **Leitura manual:** todos os exemplos foram lidos. Foram corrigidos erros de referência (valores esperados errados), pedidos ambíguos ou que não diziam o que a referência fazia, e removidas duplicatas e critérios não testáveis.
7. **Auditoria:** `experiments/dataset/auditar_dataset.py` confere estrutura, duplicatas, contaminação entre conjuntos e reexecuta todos os casos contra a referência (0 casos em que o esperado difere da referência).

Os scripts estão em [`experiments/dataset/`](../../experiments/dataset/).

## Limitações conhecidas

- O dataset é pequeno e sintético; os exercícios são de funções e classes curtas.
- A referência é escrita por um LLM: o `esperado` é a execução dela, mas a referência pode ter uma interpretação própria de um pedido ambíguo. Estimamos algo como 6% de exemplos com alguma ambiguidade residual.
- Uma verificação por amostra (segundo modelo resolvendo só pelo pedido e pela spec, em 100 dos 828 exercícios) apontou 5 exemplos do **treino** cujo pedido é ambíguo (`e0061`, `e0604`, `e0631`, `e0699` e `e0793`: valores de pontuação, chaves de um dicionário ou o que conta como token não estavam definidos). Não foram corrigidos. Nenhum deles está no teste e um (`q0029`) está na validação. Os 80 exercícios do teste foram lidos um a um e **7 têm ambiguidade** (ver `experiments/resultados/nivel1/auditoria_referencias_teste/`); nenhuma referência do teste contradiz o pedido.
- Quatro exemplos do Qwen cloud foram apontados na verificação automática depois do treino como tendo pedido ou spec menos claros (nomes de função: `ContadorCombinacoes`, `InversorBlocos`, `ComplexoTupla` e `somar_posicoes`). Foram mantidos como estão porque o modelo já tinha sido treinado com eles.

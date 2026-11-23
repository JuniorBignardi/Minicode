# Resultados da Parte 2: anexo detalhado

A versão curta, para ler primeiro, está em [`RESULTADOS.md`](RESULTADOS.md).

Este arquivo é **gerado por `experiments/gerar_resultados_md.py`** a partir dos arquivos de `experiments/resultados/`: nenhum número foi digitado à mão. Para atualizar, rode o script de novo.

## 1. Em seis linhas
1. Treinei um modelo pequeno (Qwen2.5-1,5B, com LoRA) para **escrever o plano de testes** do agente.
2. Medi com uma **prova com gabarito**: cada caso de teste é executado no código certo da tarefa.
3. **Nível 1 (a função sozinha):** o modelo passou de ~10% para ~65% de acertos, **+55 pontos**, e ficou **no mesmo nível do Qwen-14B** (~67%).
4. O 14B tem mais planos **totalmente** corretos; o 1,5B escreve bem menos testes que **nem executam**.
5. **Nível 2 (o agente completo):** o 14B sozinho acertou 88% das 25 tarefas, o híbrido com o 1,5B treinado 72% (-16 pontos, e o intervalo de confiança sustenta essa diferença) e o agente sem plano de testes 84%. **O ganho do Nível 1 não virou ganho no agente.**
6. Tudo isso com **uma execução por configuração** e 25 tarefas reais: os intervalos são largos.

## 2. O que foi medido e como
- **A prova:** cada modelo recebe o mesmo pedido, a spec e o plano de uma tarefa, e escreve casos de teste (`chamada` e `valor esperado`). O **oráculo** executa a chamada no código de referência e compara. Nota de cada caso: **correto**, **errado** ou **inavaliável** (a referência nem consegue rodar a chamada).
- **Métrica oficial (definida antes do treino):** `corretos ÷ (corretos + errados)`, uma accuracy. Os inavaliáveis ficam fora do denominador.
- **Duas provas:**
  - **Teste real:** 60 prompts das 25 tarefas da Parte 1 (referências validadas contra os testes ocultos).
  - **Teste sintético:** 80 exercícios inventados por modelos e separados antes do treino (o modelo nunca os viu).
- **Condições iguais para todos:** mesmo prompt, formato forçado por JSON Schema (como o agente faz), temperatura 0,3.
- **IC 95%:** intervalo de confiança por bootstrap sobre as tarefas. Quanto mais largo, menos firme é o número.

## 3. Nível 1: a tabela principal (métrica oficial)
**Confiança: alta.** Calculado por código sobre respostas salvas. Vale tanto quanto as referências: no teste real elas passam nos testes ocultos; no sintético, eu as li (seção 4.3).

| Modelo | Teste real (25 tarefas) | Teste sintético (80 exercícios) |
|---|---|---|
| 1,5B base | 10,2% (IC 0 a 25) | 9,2% (IC 4 a 16) |
| 1,5B base com 2 exemplos | 32,1% (IC 18 a 47) | 47,6% (IC 39 a 57) |
| **1,5B treinado (3 épocas)** | 65,0% (IC 55 a 76) | 66,8% (IC 61 a 72) |
| 1,5B treinado (melhor ponto) | 67,5% (IC 58 a 77) | 71,5% (IC 66 a 76) |
| Qwen-14B | 67,4% (IC 51 a 82) | 69,8% (IC 62 a 77) |

**Como ler:** o treino leva o modelo de ~10% para ~65%, muito acima do base e do base com 2 exemplos (que só *vê* exemplos). O 1,5B treinado e o 14B ficam no mesmo nível.
Fonte: `experiments/resultados/nivel1/*_resumo.json`.

### 3.1 Comparações pareadas (mesmas tarefas nos dois modelos)
**Confiança: alta** (aritmética com semente fixa).

| Comparação | Teste real | Teste sintético |
|---|---|---|
| ajustado (3 épocas) − base | **+54,8** pontos (IC +39 a +69) | **+57,6** pontos (IC +50 a +65) |
| ajustado (3 épocas) − base+2 exemplos | **+32,8** pontos (IC +21 a +45) | **+19,1** pontos (IC +10 a +29) |
| ajustado (3 épocas) − 14B | **-2,4** pontos (IC -16 a +11) | **-3,0** pontos (IC -11 a +5) |
| ajustado (melhor ponto) − ajustado (3 épocas) | **+2,5** pontos (IC -5 a +9) | **+4,7** pontos (IC +0 a +9) |

**Como ler:** a diferença do treinado para o base e para o base com 2 exemplos fica **longe de zero**. Contra o 14B o intervalo **contém zero**: não há diferença que se sustente.
Fonte: `experiments/resultados/nivel1/analise.md`.

## 4. Nível 1: análises complementares (feitas depois de ver os dados)
Estas **não** são a métrica oficial; servem para testar se a conclusão aguenta outras formas de medir.

### 4.1 Planos em que **todos** os casos estão certos
**Confiança: alta nos números; é uma métrica "tudo ou nada", só complementar.** Com ~5 casos por plano, até um modelo que acerta 65% dos casos teria só ~14% de planos perfeitos por pura probabilidade.

| Modelo | Real | Sintético |
|---|---|---|
| 1,5B base | 2 de 60 (3%) | 1 de 80 (1%) |
| 1,5B base com 2 exemplos | 8 de 60 (13%) | 5 de 80 (6%) |
| **1,5B treinado (3 épocas)** | 12 de 60 (20%) | 14 de 80 (18%) |
| 1,5B treinado (melhor ponto) | 13 de 60 (22%) | 13 de 80 (16%) |
| Qwen-14B | 20 de 60 (33%) | 24 de 80 (30%) |

**Como ler:** aqui o **14B vai melhor**. O 1,5B acerta a maioria dos valores, mas espalha erros em mais planos.

### 4.2 Contando os testes que não rodam como erro
**Confiança: média.** Existe uma versão sem a minha leitura (erros de nome e de sintaxe contados como erro): 63,5% contra 51,5% no teste real, a mesma conclusão.

Li um a um os 355 casos inavaliáveis do 14B, do 1,5B treinado e do base. Contei como **erro** os testes quebrados pelo próprio modelo (objeto nunca criado, texto no lugar de código), como **certos** os 14 testes válidos que o oráculo não pontua, e deixei de fora os 10 que dependem de arquivo.

| Modelo | Real: oficial → auditada | Sintético: oficial → auditada | Testes que não rodam (erro do modelo) |
|---|---|---|---|
| Qwen-14B | 67,4% → **51,7%** | 69,8% → **60,5%** | 128 |
| **1,5B treinado (3 épocas)** | 65,0% → **64,3%** | 66,8% → **65,1%** | 20 |
| 1,5B base | 10,2% → **6,7%** | 9,2% → **6,5%** | 183 |

**Como ler:** a nota do 1,5B quase não muda; a do 14B cai bastante, porque ele escreve muitos testes que nem executam. O 14B foi medido com o prompt cru, sem a revisão do plano que o agente faz.
Fonte: `experiments/resultados/nivel1/auditoria_inavaliaveis/`.

### 4.3 Sem os exercícios de teste com pedido ambíguo
**Confiança: média.** Depende da minha leitura dos 80 exercícios (ninguém conferiu depois).

Li os 80 exercícios do teste sintético: nenhuma referência contradiz o pedido e **7 têm ambiguidade** (nome de método ou formato de retorno não definidos).

| Modelo | Oficial (80 exercícios) | Sem os 7 ambíguos |
|---|---|---|
| 1,5B base | 9,2% | 10,1% |
| 1,5B base com 2 exemplos | 47,6% | 47,9% |
| **1,5B treinado (3 épocas)** | 66,8% | 68,4% |
| 1,5B treinado (melhor ponto) | 71,5% | 71,9% |
| Qwen-14B | 69,8% | 70,8% |

**Como ler:** tirar os ambíguos muda as notas em no máximo ~2 pontos e não troca a ordem dos modelos.
Fonte: `experiments/resultados/nivel1/auditoria_referencias_teste/`.

## 5. O que o Nível 1 **não** prova
- Só 25 tarefas reais: os intervalos são largos.
- O oráculo é tão bom quanto a referência. No teste real as referências passam nos testes ocultos; no sintético, li as 80 (seção 4.3).
- A leitura dos inavaliáveis e dos 80 exercícios é **julgamento meu**, reproduzível (os vereditos estão salvos), mas não é teste automático.
- "Comparável ao 14B" **não** é "melhor que o 14B".

## 6. Nível 2: o agente completo nas 25 tarefas
**Confiança: alta no que aconteceu** (quem passou no teste oculto) e **baixa para generalizar** (uma execução por configuração).

O agente roda cada tarefa e o **teste oculto** decide se está correta. Três versões do mesmo agente: **A** = Qwen-14B sozinho; **B** = o 1,5B treinado escreve a primeira versão do plano de testes e o 14B faz o resto; **C** = sem a etapa do plano de testes (ablação).

### Nível 2: agente completo (25 tarefas)

| configuração | execuções | TaskSuccessRate (IC 95%) | por repetição | FirstAttempt | iterações | chamadas ao LLM | s/tarefa | erros de infraestrutura | usou o especialista |
|---|---|---|---|---|---|---|---|---|---|
| A: 14B sozinho | 25 (+0 com erro de infra) | **88,0%** (72 a 100) | 88% | 64% | 17,6 | 17,6 | 186 | 0 | - |
| B: 14B + 1,5B ajustado no plano de testes | 25 (+0 com erro de infra) | **72,0%** (52 a 88) | 72% | 44% | 23,4 | 23,4 | 269 | 0 | 25/25 |
| C: sem plano de testes (ablação) | 25 (+0 com erro de infra) | **84,0%** (68 a 96) | 84% | 64% | 14,9 | 14,9 | 140 | 0 | - |

## Diferenças em relação ao A (pareadas por tarefa; bootstrap sobre as 25 tarefas)

| comparação | diferença em pontos (IC 95%) | leitura |
|---|---|---|
| B − A | -16,0 (-32 a -4) | intervalo não contém 0 |
| C − A | -4,0 (-16 a +8) | intervalo contém 0: não dá para afirmar diferença |

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


### Qualidade do plano de testes que o agente usou × resultado da tarefa

O plano final gravado pelo agente (`test_plan.md`) pontuado pelo oráculo. "Plano com erro" = pelo menos um caso com valor esperado errado.

| configuração | execuções | valores corretos no plano | planos sem nenhum erro | tarefas corretas com plano SEM erro | tarefas corretas com plano COM erro |
|---|---|---|---|---|---|
| A | 25 | 77,9% (60/77) | 16/25 | 15/16 | 7/9 |
| B | 25 | 64,6% (73/113) | 8/25 | 5/8 | 13/17 |

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


**Ressalvas do Nível 2:** uma execução por configuração; a Parte 1 mediu até 20 pontos de ruído entre rodadas; as três configurações rodaram juntas no mesmo servidor, então os tempos por tarefa **não são comparáveis** entre elas.

## 7. De onde vem cada número
| O quê | Arquivo |
|---|---|
| Acerto de cada modelo | `experiments/resultados/nivel1/<modelo>_resumo.json` |
| Cada caso com a nota do oráculo | `experiments/resultados/nivel1/<modelo>_avaliacao.jsonl` |
| Prompt e resposta completos | `experiments/resultados/nivel1/<modelo>_respostas.jsonl` |
| Comparações pareadas | `experiments/resultados/nivel1/analise.md` |
| Casos inavaliáveis lidos | `experiments/resultados/nivel1/auditoria_inavaliaveis/` |
| Referências do teste sintético | `experiments/resultados/nivel1/auditoria_referencias_teste/` |
| Curvas de perda do treino | `experiments/resultados/treino/` |
| Agente completo (A, B, C) | `experiments/resultados/nivel2/` |

## 8. Glossário
- **Oráculo:** o código de referência de uma tarefa, usado como gabarito: executa a chamada do caso e devolve o valor certo.
- **Accuracy (aqui):** fração dos casos cujo valor esperado bate com o do gabarito.
- **Inavaliável:** caso que o gabarito não consegue executar, então não dá para dizer se o modelo acertou.
- **IC 95%:** faixa em que o valor verdadeiro provavelmente está; se a diferença entre dois modelos tem um IC que contém zero, não se pode afirmar que são diferentes.
- **Pareado:** comparação em que cada tarefa é medida nos dois modelos, o que é mais sensível que comparar as médias.
- **Ablação:** tirar um componente para ver se ele fazia diferença (aqui, a etapa do plano de testes).

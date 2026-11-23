# Hipótese experimental da Parte 2

Este texto foi escrito em 22/11/2026, **antes** de treinar qualquer modelo. A hipótese, as métricas e os critérios de refutação não mudam depois de ver os resultados.

## 1. De onde vem a hipótese (Parte 1)

Rodamos o MiniCode com o Qwen 14B em 60 execuções (3 rodadas do conjunto difícil e 2 do fácil, 25 tarefas) e conferimos cada erro contra uma solução de referência executável (as 25 referências foram validadas contra os verificadores ocultos da Parte 1).

- 14 das 60 execuções terminaram com resultado errado (23%).
- A primeira versão do código estava certa em 93% das tarefas de código (52 de 56). Escrever código e usar as ferramentas não é o gargalo (10% das chamadas de ferramenta deram erro, e isso não separa as execuções certas das erradas).
- O gargalo está nos **testes**: em 10 das 14 execuções com resultado errado, o agente escreveu testes que falham até na solução de referência.
- No **plano de testes**, o 14B escreveu valores esperados errados em **72 de 188 casos avaliáveis (38%)**; 63 casos a mais não puderam ser executados pela referência e ficaram de fora. O erro concentra-se em algumas tarefas (por exemplo `mesclar_intervalos`: 14 de 16; `validar_senha`: 12 de 15; `fibonacci`: 11 de 21).
- Esses erros se propagam: o diagnóstico do 14B contradisse o oráculo em 64% das execuções com resultado errado e, quando o erro estava antes do código, culpou o código em 22 de 36 casos (61%); em 12 disse que o erro era do teste ou do plano (a classificação certa) e em 2 não decidiu. O agente então "conserta" um código que estava certo.

Conclusão: o ponto onde o erro nasce é o **plano de testes** (os valores esperados). O diagnóstico errado é uma consequência. Uma versão anterior deste texto escolhia o diagnóstico como função a especializar; trocamos porque a medida mostrou que corrigir a origem (o valor esperado) é mais direto, e porque ela tem métrica automática simples. O ajuste do diagnóstico fica como trabalho futuro.

## 2. Função escolhida (uma só, como pede o enunciado)

**Geração do plano de testes.** Entrada: pedido do usuário, especificação e plano de implementação (exatamente o prompt que o agente envia hoje, `mensagens_plano_de_testes`). Saída: JSON `{"casos": [{"criterio", "entrada", "esperado"}]}`, com pelo menos um caso por critério de aceitação.

## 3. Hipótese

**H1 (principal).** O fine-tuning com LoRA de um Qwen2.5 pequeno (1,5B; 0,5B e 3B como comparação de escala, se o tempo permitir) para gerar o plano de testes **aumenta a fração de casos com valor esperado correto** em relação ao mesmo modelo sem fine-tuning.

**H0 (nula).** O modelo ajustado não é melhor que o modelo base: aprende só o formato do JSON, não a calcular o valor correto.

**H2 (secundária).** O modelo ajustado atinge fração de casos corretos igual ou maior que a do Qwen-14B com o prompt atual (62%, medido na Parte 1).

**H3 (Nível 2).** Trocar a chamada do plano de testes do MiniCode pelo modelo especializado muda o TaskSuccessRate do agente. Não há direção prevista: o enunciado lembra que melhorar a métrica da função não garante melhorar o sistema. Comparação: agente A (14B sozinho), B (14B com o especialista no plano de testes) e C (ablação: sem a etapa do plano de testes).

## 4. Como será medido

- **Oráculo:** cada caso (`entrada`, `esperado`) é executado na solução de referência da tarefa. O caso é **correto** se o valor da referência é igual ao esperado, **errado** se é diferente, **inavaliável** se a referência não consegue executar a entrada. A comparação é a do `oraculo.py` da Parte 2 (a mesma que gerou os 38% acima).
- **Métrica principal:** fração de casos avaliáveis com valor esperado correto.
- **Métricas secundárias:** fração de planos válidos (JSON válido e todos os critérios cobertos), fração de casos inavaliáveis, e fração de tarefas com todos os casos corretos.
- **Conjuntos de teste (nunca usados no treino nem na escolha de hiperparâmetros):**
  1. **Teste real (principal):** os pares (pedido, spec, plano) que o 14B realmente recebeu nas 25 tarefas do benchmark, gravados nas 60 execuções, com a referência de cada tarefa como oráculo. O intervalo de confiança é por bootstrap sobre as tarefas.
  2. **Teste sintético:** 10% dos exercícios gerados, separados por exercício antes do treino.
- **Linhas de comparação:** (1) Qwen-14B com o prompt atual (62%, dos logs); (2) modelo pequeno base; (3) modelo pequeno ajustado. Se houver tempo: (4) pequeno base com dois exemplos no prompt, o baseline barato que o fine-tuning precisa superar.
- **Curva de escala (secundária):** treinar com 25%, 50% e 100% dos exemplos para ver se mais dados ainda ajudam.

## 5. Critérios definidos antes do treino

| Resultado no teste real | Conclusão |
|---|---|
| ajustado ≥ base + 15 pontos, com o intervalo de confiança separado do base | H1 confirmada |
| ajustado < base + 5 pontos | H1 refutada (resultado negativo, que será reportado) |
| entre os dois | inconclusivo |
| ajustado ≥ 62% (14B) | H2 confirmada |

## 6. Dados de treino (resumo; o detalhe vai no relatório)

Exercícios de programação inventados por modelos professores (Nemotron 3 Ultra e Nemotron 3.5 Super, via API gratuita da NVIDIA, e DeepSeek v4.1 Flash, via Qwen cloud, para fins acadêmicos). O professor escreve o pedido, a solução de referência, a spec (sem os resultados), o plano e as **entradas** dos casos. Os **valores esperados vêm da execução da solução de referência pelo nosso programa, nunca do modelo**. Exercícios com código que não executa, não determinístico, com saídas pouco variadas, parecidos com as 25 tarefas do benchmark ou que repetem um exercício já aceito são descartados. O modelo professor não é o Qwen-14B (o enunciado diz que o 14B "poderá" ser usado).

## 7. Limites assumidos

- **O teste real é pequeno** (25 tarefas, concentrado em poucas). O ruído entre rodadas do agente chegou a ±20 pontos; o Nível 2 deve ser lido com esse cuidado.
- **Erros que vêm da spec:** em pelo menos 22% dos casos errados de teste o valor errado já está escrito na spec. Um plano fiel a uma spec errada também é "errado" para o oráculo e o especialista sozinho não corrige isso. Reportaremos o resultado também no subconjunto sem valor errado na spec.
- **O agente atual não corrige a spec:** não há transição de volta para a spec. Um laço de correção de spec é trabalho futuro.
- As 25 tarefas do benchmark foram usadas no desenvolvimento do agente e dos experimentos (e como oráculo); nenhuma entra no treino, mas elas orientaram esta escolha.
- Os exercícios sintéticos vêm de outros modelos, com viés de estilo próprio, e as tarefas de teste real são de outro tipo (mais curtas). Por isso o teste real é o principal.
- O oráculo depende de a referência estar correta; os 63 casos não executáveis pela referência ficam fora das métricas.
- O dataset final tem 754 exemplos de treino, 79 de validação e 80 de teste, todos lidos um a um, com as referências erradas corrigidas e a divisão feita por exercício antes do treino (ver `datasets/plano_de_testes/README.md`). Ele está no repositório, em `datasets/plano_de_testes/`, junto com os scripts de geração em `experiments/dataset/`. A publicação foi decidida pelo grupo, que concluiu que os termos de uso das APIs usadas permitem.

## 8. Resultados e veredito (escrito depois do experimento)

### 8.1 Protocolo executado
Os 60 prompts reais e os 80 sintéticos foram dados a cada modelo com o **mesmo prompt, o formato forçado por JSON Schema (como o agente faz) e temperatura 0,3**, e pontuados pelo oráculo. Todos os arquivos estão em `experiments/resultados/nivel1/` (prompt e resposta completos de cada chamada, nota de cada caso).

| Modelo | Papel | Real (IC 95%) | Sintético (IC 95%) |
|---|---|---|---|
| 1,5B base | baseline | 10,2% (0 a 24) | 9,2% (4 a 16) |
| 1,5B base com 2 exemplos | baseline barato (linha 4 da seção 4) | 32,1% (18 a 47) | 47,6% (39 a 57) |
| **1,5B + LoRA, 3 épocas** | experimento | **65,0%** (55 a 76) | **66,8%** (61 a 72) |
| 1,5B + LoRA, melhor ponto da validação | variante | 67,5% (58 a 77) | 71,5% (66 a 76) |
| Qwen-14B | referência | 67,4% (51 a 83) | 69,8% (62 a 77) |

Comparações **pareadas** (mesmas tarefas nos dois modelos, bootstrap sobre tarefas), em pontos: ajustado − base = **+55** (IC +39 a +69) no real e +58 no sintético; ajustado − base com 2 exemplos = **+33** (+21 a +45) e +19; ajustado − 14B = −2 (−16 a +11) e −3 (−11 a +5). Melhor ponto − 3 épocas: +3 (−5 a +9) e +5 (0 a +9). Detalhes e a métrica estrita em `experiments/resultados/nivel1/analise.md`.

### 8.2 Veredito
- **H1: confirmada.** O ajustado ficou 55 pontos acima do base no teste real, com o intervalo da diferença longe de zero, bem acima do limiar de +15 definido na seção 5. Ficou também acima do base com 2 exemplos (+33), então o ganho não é só aprender o formato nem só ver exemplos. **H0 refutada.**
- **H2: confirmada pelo critério definido** (ajustado ≥ 62%: 65,0% no real). Contra o 14B medido hoje no mesmo protocolo (67,4%), o ajustado é **comparável**: a diferença (−2 pontos) está dentro do ruído, e não afirmamos que seja melhor. O 14B dos logs da Parte 1 (61,2%) foi medido em outro servidor, dentro do agente e sem o mesmo protocolo; o 14B de hoje serve de calibração e fica dentro do intervalo daquele valor.
- **H3 (Nível 2): o resultado é negativo.** A hipótese não previa direção. O agente com o especialista (B) acertou 72% das 25 tarefas contra 88% do 14B sozinho (A): −16 pontos, com intervalo pareado de −32 a −4, que não contém zero. Sem a etapa do plano de testes (C, a ablação), o agente acertou 84% (−4 pontos contra A, intervalo de −16 a +8, que contém zero). **Ou seja, empatar com o 14B no Nível 1 não se traduziu em ganho no agente**, o que é exatamente a distinção que o enunciado pede. Nos planos que o agente realmente usou, os do B tinham mais valores errados (64,6% corretos contra 77,9% no A), mas isso não explica tudo: 3 das 8 tarefas do B com plano sem erro também falharam. Limitação: uma execução por configuração, e a Parte 1 mediu até 20 pontos de ruído entre rodadas. Os dados estão em `experiments/resultados/nivel2/`.

### 8.3 Subconjunto sem valor errado na spec (compromisso da seção 7)
Aproximação: um caso errado é "herdado da spec" quando o valor errado aparece escrito na spec do prompt. No teste real, **23% dos erros do ajustado, 32% dos do 14B e 44% dos do base** são herdados. Sem eles, a nota vai a 70,8% (ajustado), 75,2% (14B) e 17,0% (base); no sintético, 70,6%, 72,6% e 13,7%. A ordem entre os modelos não muda e a diferença entre ajustado e 14B segue pequena (não calculamos intervalo para este subconjunto). A aproximação é grosseira: um valor curto pode aparecer na spec por coincidência.

### 8.4 Casos que o oráculo não consegue julgar
O 14B escreveu muitos casos que a referência nem executa (65 no real e 69 no sintético, contra 18 e 14 do ajustado). Os 355 casos "inavaliáveis" do 14B, do ajustado e do base foram lidos um a um (`experiments/resultados/nivel1/auditoria_inavaliaveis/`): 331 são testes quebrados pelo próprio modelo, 14 eram válidos e corretos, 10 dependem de arquivos. Contando os quebrados como erro, a nota do ajustado quase não muda (64,3% real, 65,1% sintético) e a do 14B cai (51,7% e 60,5%). A nota oficial continua sendo a definida antes; esta é uma análise de sensibilidade, feita depois de ver os dados.

### 8.4b Auditoria das referências do teste sintético
Os 80 exercícios do teste sintético foram lidos um a um (pedido, spec e referência). **Nenhuma referência contradiz o pedido; 7 exercícios têm ambiguidade** (nomes de métodos, formato de retorno ou assinatura não definidos, 60 dos 672 casos). Tirá-los da conta muda as notas em no máximo 1,6 ponto e não altera a ordem entre os modelos (`experiments/resultados/nivel1/auditoria_referencias_teste/`). No teste real, as referências foram validadas contra os verificadores ocultos da Parte 1.

### 8.5 O que mudou em relação ao plano e o que não foi feito
- **Mudou o protocolo:** a primeira avaliação (Colab) foi feita **sem** schema e deu 0% de planos legíveis para o base. O agente real sempre usa schema, então essa comparação media o formato, não o conteúdo. Ela ficou como resultado secundário (`resultados/colab_sem_schema/`) e a comparação principal passou a ser a descrita em 8.1.
- **Foram acrescentadas depois de ver os dados** (não estavam na seção 4): a variante "melhor ponto da validação", as comparações pareadas, a métrica estrita e a auditoria dos inavaliáveis. Por isso são análises complementares, não confirmações.
- **Não foi feito:** a curva de escala (25%, 50% e 100% dos dados) e as comparações de tamanho do modelo (0,5B e 3B). A seção 3 as previa "se o tempo permitir", e não permitiu.
- **Duas execuções de treino:** o adaptador principal (3 épocas) vem de `notebooks/train.ipynb`; o `notebooks/train_checkpoints.ipynb` repete o treino com um adaptador por época e retorna ao melhor ponto da validação (passo 175). A curva de perda de validação para de cair por volta do passo 175 (0,140) e sobe um pouco (0,154): sobreajuste leve na terceira época.
- **Quatro exemplos do Qwen cloud** foram apontados, depois do treino, como tendo pedido ou spec menos claros; foram mantidos porque o modelo já tinha sido treinado com eles.

# Auditoria das referências do teste sintético (80 exercícios)

Cada um dos 80 exercícios do conjunto de teste foi lido por inteiro (pedido, spec, código da referência e casos), sem executar nada: o código é determinístico, então se a referência cumpre o pedido o valor `esperado` está certo. O veredito de cada exercício está em `vereditos.json`.

Vereditos possíveis: **ok** (a referência cumpre o pedido e a spec), **erro** (o código contradiz o pedido) e **amb** (o pedido ou a spec não definem algo que os casos testam, por exemplo o nome de um método).

## Resultado
- **73 ok, 7 ambíguos, 0 erros de referência.**
- Os ambíguos têm 60 dos 672 casos do conjunto.

| # | Exercício | Ambiguidade |
|---|---|---|
| 15 | `FilaMensagens` | `pendentes()` depois de `desenfileirar()` sem confirmar: o pedido diz "ainda não confirmadas", a referência devolve `[]` (1 caso de 10) |
| 27 | `serializar_registros` | se a saída termina ou não em quebra de linha (1 caso de 9) |
| 46 | `Classificacao` | o método `adicionar` e o atributo `itens` não são nomeados (8 casos de 8) |
| 50 | `Matricula` | o formato de `listar_alunos()` (pares nome e nota) não é definido (1 caso de 6) |
| 57 | `LimpadorTexto` | o nome do método (`limpar`) e o tipo do retorno não são definidos (9 casos de 9) |
| 59 | `CabecalhoHTTP` | os métodos `obter`, `contem` e `nomes` não são nomeados (7 casos de 10) |
| 70 | `matricula_aluno` | a assinatura e a estrutura da turma não são definidas (8 casos de 8); a "média mínima 6,0" do pedido não é usada pela referência |

Também ficaram registrados como riscos latentes, sem caso que os exercite: "tres" sem acento e "catorze" em `extenso` (#56), códigos 100 a 199 em `StatusHTTP` (#49) e o pedido mal formulado de `vencimentos_por_mes` (#21), que a spec desfaz.

## Efeito nos números do Nível 1 (teste sintético, valores corretos)

| Modelo | Oficial (80 exercícios) | Sem os 7 ambíguos | Sem os 5 piores (#46, #50, #57, #59, #70) |
|---|---|---|---|
| 1,5B base | 9,2% | 10,1% | 9,6% |
| base com 2 exemplos | 47,6% | 47,9% | 47,8% |
| ajustado (3 épocas) | 66,8% | 68,4% | 67,6% |
| ajustado (melhor ponto) | 71,5% | 71,9% | 71,9% |
| Qwen-14B | 69,8% | 70,8% | 70,4% |

Tirar os exercícios ambíguos mexe nos números em no máximo 1,6 ponto e não muda a ordem entre os modelos. A conclusão do Nível 1 não depende deles.

## O que esta auditoria não prova
Foi uma leitura humano-equivalente (feita pelo assistente de IA do projeto), não um teste automático, e pode ter deixado passar um erro sutil. Para o teste real (25 tarefas) a referência é outra: foi validada contra os verificadores ocultos da Parte 1.

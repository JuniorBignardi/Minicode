# Arquitetura do MiniCode

Este documento explica **por que** o sistema é como é. O resumo para usar o agente está no [README](../README.md).

## 1. Princípio de projeto: quem faz o quê

Baseado nas aulas práticas de tool calling e agentes:

> O LLM **não executa**, ele **escolhe ações**. **Regra crítica e verificável é código; interpretação, síntese e redação é modelo.**

| Responsabilidade | Modelo (Qwen 14B) | Harness (código) |
|---|---|---|
| Entender o pedido, escrever spec, plano, plano de testes, código e testes | ✅ | |
| Escolher a próxima ação (JSON) | ✅ | valida o formato (JSON Schema) |
| Dizer quais ferramentas existem em cada estado | | ✅ (`FERRAMENTAS_POR_ESTADO`) |
| Executar ferramentas, ler/gravar arquivos | | ✅ |
| Rodar os testes e decidir `DONE` | | ✅ |
| Conferir cobertura dos critérios pelo plano de testes | | ✅ |
| Recusar escritas inválidas (teste protegido, Python quebrado, perda de testes) | | ✅ |
| Contar iterações, tentativas, leituras; detectar repetição | | ✅ |
| Montar o contexto que o modelo vê (diff, estado atual, diagnóstico) | | ✅ |
| Julgar se um artefato cumpre a spec | ✅ (como **opinião**, com orçamento de veto) | decide quanto a opinião vale |
| Calcular valores esperados de testes | ✅ (e erra) | a execução dos testes corrige |

Duas consequências práticas:

- **Schema garante a forma, nunca o conteúdo.** O `response_format` impede JSON inválido e ferramenta fora do `enum`, mas não impede uma decisão errada.
- **Juízes LLM não são oráculos.** O oráculo é a execução. Um juiz pode atrasar o `DONE` no máximo uma vez por critério.

## 2. Máquina de estados

Estados: `RECEIVED`, `SPECIFIED`, `PLANNED`, `TEST_PLANNED`, `IMPLEMENTING`, `VERIFYING`, `DIAGNOSING`, `REPAIRING`, `DONE`, `FAILED`.

| De | Para | Condição (hard gate) |
|---|---|---|
| `RECEIVED` | `SPECIFIED` | existe uma spec |
| `SPECIFIED` | `PLANNED` | existe um plano |
| `PLANNED` | `TEST_PLANNED` | existe um plano de testes |
| `PLANNED` | `IMPLEMENTING` | (ramo sem plano de testes: o plano não saiu ou `planejar_testes=False`) |
| `TEST_PLANNED` | `IMPLEMENTING` | |
| `IMPLEMENTING` | `VERIFYING` | ≥ 1 arquivo alterado e todo `.py` citado no pedido existe no caminho exato (é o `finish` aceito) |
| `VERIFYING` | `DONE` | testes passaram e, com revisão ligada, as duas revisões aprovadas |
| `VERIFYING` | `DIAGNOSING` | os testes falharam (não passaram) e o diagnóstico está ligado |
| `VERIFYING` | `REPAIRING` | falha de teste ou de revisão, e ainda há tentativas |
| `DIAGNOSING` | `REPAIRING` | existe um diagnóstico |
| `DIAGNOSING` | `TEST_PLANNED` | o diagnóstico apontou o plano de testes (`PLAN_BUG`) |
| `TEST_PLANNED` | `REPAIRING` | só durante um reparo, com diagnóstico |
| `REPAIRING` | `IMPLEMENTING` | |
| qualquer | `FAILED` | limite de iterações ou de tentativas, ou erro da LLM |

Só o orquestrador chama `avancar()`; as transições e gates ficam todos em `agent/maquina/estados.py`, num lugar só, o que facilita testá-los (`tests/test_estados.py`).

## 3. Os passos do orquestrador

O orquestrador é uma sequência de passos pequenos, dividida em módulos coesos (regra do projeto: nenhum arquivo de código passa de 400 linhas, garantida por `tests/test_estrutura.py`):

| Módulo | Passos |
|---|---|
| `agent/orquestrador.py` | `rodar_agente` (a sequência) e `implementar_e_reparar` (o laço central) |
| `agent/etapas/planejamento.py` | `fazer_spec`, `fazer_plano`, `fazer_plano_de_testes` |
| `agent/etapas/verificacao.py` | `verificar`, `revisar`, `veto_valido` |
| `agent/etapas/reparo.py` | `diagnosticar_falha`, `corrigir_plano_de_testes`, `descartar_testes_que_continuam_falhando`, `montar_mensagens_do_reparo` |
| `agent/maquina/controle.py` | `avancar` (único que muda o estado), `finalizar` |

Cada passo devolve `False` se a execução já falhou:

```
fazer_spec ─▶ fazer_plano ─▶ fazer_plano_de_testes ─▶ implementar_e_reparar ─▶ finalizar
```

`implementar_e_reparar` é o laço central:

```
repetir:
    rodar_fase_implementacao        # a LLM lê/escreve até pedir finish
    verificar                       # revisão do código → pytest → revisão dos testes
    DONE?  → sair
    falha: repetiu = assinatura da falha já foi vista?
    se falha de teste: diagnosticar_falha        (estado DIAGNOSING)
    se PLAN_BUG: corrigir_plano_de_testes        (estado TEST_PLANNED)
    avançar para REPAIRING; remover os testes errados; montar o contexto do reparo
    voltar para IMPLEMENTING
```

## 4. Contexto: quando continuar a conversa e quando recomeçar

A conversa cresce a cada passo e é reenviada inteira (custo aproximadamente quadrático), e uma regra enterrada em mensagens `user` perde força para os resultados de ferramenta. Por isso:

| Etapa | Contexto | Motivo |
|---|---|---|
| Spec | conversa própria; a revisão é acrescentada | é a **revisão de um rascunho**: o modelo precisa ver o que escreveu |
| Plano, plano de testes | conversa nova por fase; recebe só o artefato anterior | só o documento importa, não a transcrição |
| Revisões e diagnóstico | **sempre contexto novo** | independência: o juiz não vê as racionalizações do autor |
| Implementação | uma conversa com ferramentas | é o laço de agente (ReAct): precisa das observações |
| Reparo | continua a conversa, **ou recomeça** quando o programa removeu testes errados ou na última tentativa | o histórico contém o artefato errado e o modelo o copia de volta |

Consequência importante: como cada fase tem contexto novo, **a conversa da implementação não herda o que a spec leu**. Por isso existe o gate "ler antes de sobrescrever": sem ele o modelo gravava arquivos que nunca tinha visto.

Entre fases passam **artefatos**, não conversas: spec, plano, plano de testes, estado atual dos arquivos, diff contra o original e o diagnóstico.

## 5. Os "juízes" e o orçamento de veto

Há chamadas ao modelo que julgam em vez de gerar:

| Chamada | Pergunta | Quem decide |
|---|---|---|
| Revisão da spec | a spec cobre cada requisito do pedido? | só pode mandar reescrever (até 2×) |
| Revisão do plano de testes | o valor esperado de cada caso está certo? | só pode mandar reescrever (até 2×) |
| Revisão do código | o código cumpre cada critério **sobre o código**? | veto com orçamento |
| Revisão dos testes | os testes seguem o plano e cobrem os critérios? | veto com orçamento |
| Diagnóstico | quem errou: código, teste, plano ou ambiente? | classifica; o programa age |

Regras que valem para todos os juízes:

- A resposta é um JSON Schema com **booleanos por critério**; o programa lê os campos (nunca uma frase do modelo).
- A revisão do código separa critérios que **não são sobre o código** (campo `sobre_o_codigo`): um critério como "os testes devem passar" não pode ser verificado lendo o código e não reprova.
- **Orçamento de veto:** cada critério só pode ser reprovado uma vez, com efeito, por revisão. Depois disso a reprovação é dispensada (`revisao_dispensada`) e os testes decidem. Justificativa: um juiz é uma opinião; se o reparo não o satisfez, ou ele está errado ou o modelo não consegue, e esperar mais não ajuda.
- O diagnóstico só vale se **citar um trecho verdadeiro** da spec; senão vira `UNKNOWN`.
- Os juízes recebem o **pedido original** além da spec, com a regra "se divergirem, vale o pedido": a spec é um artefato derivado e pode ter derivado do que o usuário pediu.
- O modelo é instruído a responder em português (os juízes às vezes respondiam em inglês).

Custo conhecido: o orçamento de veto também dispensa vetos corretos (ocorreu no `contar linhas`).

## 6. Repair loop

```
VERIFYING ──pytest falhou──▶ DIAGNOSING ──┬─ CODE_BUG ───────────────▶ REPAIRING (só código)
                                          ├─ TEST_BUG ──(remove o teste)─▶ REPAIRING (só testes)
                                          └─ PLAN_BUG ─▶ TEST_PLANNED ─▶ REPAIRING (só testes)
          ──revisão reprovou (veto válido)──────────────────────────────▶ REPAIRING
```

Detalhes:

- **Remoção do teste errado.** O modelo regravava o mesmo teste (30/30 repetições idênticas, com temperatura 0,3, 0,5 e 0,7). O programa apaga a função de teste que falhou (AST) e recomeça a conversa sem o texto antigo. Testes que já existiam no projeto nunca são tocados.
- **Escalonamento de etapa.** O programa guarda a *assinatura* de cada falha (as linhas `E ...` do pytest, sem nome de arquivo nem tempo). Se uma falha já vista volta e o diagnóstico era `TEST_BUG`, a origem está uma etapa acima: vira `PLAN_BUG`.
- **Restrição do diagnóstico:** o reparo só pode alterar o lado apontado. A restrição é levantada depois de 2 escritas recusadas (para não consumir todas as iterações) ou se o reparo anterior não mudou nada.
- **Diff contra o original.** Na primeira escrita sobre um arquivo existente, o programa guarda o conteúdo original. O reparo mostra o diff: reescrever um arquivo inteiro de memória fazia o modelo mudar o comportamento sem perceber (ex.: `1 + taxa` virou `1 + taxa/100` numa refatoração).
- **Hierarquia de confiança dos oráculos.** Testes que já existiam no projeto são confiáveis; os escritos pelo modelo não são. Quando as tentativas acabam e o último diagnóstico aponta o teste (`TEST_BUG` ou `PLAN_BUG`), `descartar_testes_que_continuam_falhando` roda o pytest completo, remove os testes do modelo que falham, revisa o código e roda o pytest de novo. Se passar, o `DONE` vale (continua exigindo testes passando) e o descarte é registrado (`testes_descartados`) e mostrado. Medição que motivou isso: 7 de 16 execuções `FAILED` tinham o código correto em disco.
- **Tentativas:** no máximo 3 reparos (`max_tentativas`). Voltar para `TEST_PLANNED` consome uma tentativa.

## 7. Vícios observados no Qwen 14B e contramedidas

Esta é a tabela que justifica as peças "a mais" do harness. Cada linha nasceu de uma falha vista nos benchmarks.

| Vício do modelo | Evidência | Contramedida |
|---|---|---|
| Regrava o mesmo artefato errado | 30/30 regravações idênticas; 20 recusas seguidas | remover o teste errado + contexto novo + escalonar a etapa |
| Erra aritmética nos valores esperados | `4.414` em vez de `3.414`; `16` em vez de `14` | a execução é o árbitro: teste falha contra código revisado → `PLAN_BUG` |
| Superespecifica (texto de mensagem de erro, formatos, critérios sobre os próprios testes) | `str(KeyError)` com aspas; "os testes devem passar" na spec | plano só com o que a spec define; revisor classifica `sobre_o_codigo`; orçamento de veto |
| Reescreve arquivo inteiro e muda o comportamento | `taxa` virou `taxa/100` | diff contra o original no reparo |
| Sobrescreve um arquivo que nunca leu | 11 de 51 sobrescritas (22%) foram às cegas; `servico.py` perdeu `criar_usuario` | **gate "ler antes de sobrescrever"**: o programa registra o que o modelo viu na conversa atual e recusa a escrita com a instrução exata (`read_file`) |
| Culpa um teste que já existia no projeto | o diagnóstico mandou "mudar" `test_original.py` | o programa corrige para `CODE_BUG`: teste do projeto é oráculo confiável |
| Teste usa arquivo que não cria | `FileNotFoundError: exemplo.txt` | regra no prompt (`tmp_path`) e no plano de testes |
| Entrada que viola várias regras esperando só uma | `validar_senha('abc')` esperando `['curta']` | regra no plano: a entrada cumpre as outras regras |
| Juízes reprovam o certo e aprovam o errado | 3 de 4 falhas de uma rodada vieram de reprovação impossível de atender | orçamento de veto; testes como oráculo; juízes em contexto novo |
| Lê ambiguidade do pedido de forma errada e todas as camadas herdam o erro | `list` virou `str` no `contar linhas` | **sem contramedida programática**; é limitação documentada |
| Escapa `\n` duas vezes no código | 3 de 293 execuções | `desescapar_conteudo` |
| Laços de exploração e chamadas repetidas | leituras em loop | limite de leituras, recusa de chamada repetida, limite de iterações |
| Pytest com acentos corrompidos faz o modelo "diagnosticar" encoding | `maçã` virava `maÃ§Ã£` | saída lida em UTF-8 |
| Usa mal ferramentas de edição por trecho | `replace_text` com `old` inexato; 9 edições com sintaxe inválida | removido; `create_file` + `write_file` com gates |

## 8. Resultados negativos (para a seção de análise)

Estes experimentos não melhoraram o resultado e foram removidos ou simplificados: `replace_text`; temperatura crescente no reparo; varredura de temperatura; modelo de 7B; prompts com exemplos de tarefas; ancoragem do diagnóstico como único filtro. Cada um está resumido no README.

## 9. Rastreabilidade

`.minicode/` por execução: `specification.md`, `plan.md`, `test_plan.md`, `actions.jsonl` (um evento por linha), `state.json` e, em modo de depuração, `debug.jsonl`.

Eventos mais úteis em `actions.jsonl`:

| Evento | Quando |
|---|---|
| `mudanca_estado` | toda transição |
| `ferramenta` | cada ferramenta chamada, com argumentos e resultado |
| `finish_recusado` | um hard gate barrou o `finish` |
| `escrita_protegida`, `escrita_restrita`, `escrita_invalida`, `escrita_perde_testes`, `escrita_sem_mudanca` | cada gate de escrita |
| `testes`, `revisao`, `revisao_dispensada` | verificação |
| `diagnostico`, `reparo`, `reparo_escalado`, `plano_de_testes_corrigido`, `testes_removidos`, `contexto_reiniciado` | repair loop |
| `resultado_final` | estado, tentativas, iterações, chamadas |

## 10. Tolerância a falhas do modelo

O executor trata o modelo como fonte **não confiável**: ferramenta fora da allowlist, argumentos faltando ou extras e erros viram **observações de erro** que o modelo pode ler e corrigir, em vez de exceções que derrubam o programa. A chamada ao endpoint tem tempo limite e erro de rede vira `FAILED` com o motivo registrado.

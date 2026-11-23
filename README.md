# MiniCode

## 🎥 Vídeo de demonstração

Confira o vídeo abaixo para conhecer o funcionamento do projeto.

[![Assistir à demonstração do projeto](https://img.youtube.com/vi/zHvtjiy3MgQ/maxresdefault.jpg)](https://youtu.be/zHvtjiy3MgQ)

Agente de programação simplificado, inspirado no Claude Code, desenvolvido como trabalho da disciplina de Redes Neurais Artificiais (Parte 1). Dado um pedido em linguagem natural, o MiniCode lê o projeto, escreve uma **especificação** e um **plano**, define os **testes** antes do código, implementa, roda os testes e **repara** os erros, tudo sob controle de um harness programático.

A ideia central do trabalho: **a LLM propõe, o programa decide.** O modelo escolhe ações em JSON; quem valida, executa, restringe e registra é o código.

```
pedido ─▶ SPEC ─▶ PLANO ─▶ PLANO DE TESTES ─▶ IMPLEMENTAÇÃO ─▶ VERIFICAÇÃO ─▶ DONE
                                                   ▲               │ falhou
                                                   └── REPARO ◀── DIAGNÓSTICO
```

Documentação detalhada: [docs/architecture.md](docs/architecture.md) · avaliação: [eval_tasks/README.md](eval_tasks/README.md) · **Parte 2 (fine-tuning): [seção 12](#12-parte-2-especializando-uma-llm)** · uso de IA: [AI_USAGE.md](AI_USAGE.md).

## 1. Como executar

Requisitos: Python 3.10+ e acesso a um endpoint OpenAI-compatível com um modelo Qwen (a disciplina fornece o de ~14B).

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows (PowerShell)

pip install -e ".[dev]"

cp .env.example .env               # Windows (PowerShell): copy .env.example .env
                                   # preencha os valores; o .env nunca vai para o git
pytest                             # 300+ testes, sem chamar a LLM
```

| Variável | Descrição |
|---|---|
| `MINICODE_API_BASE` | URL base do endpoint OpenAI-compatível |
| `MINICODE_API_KEY` | chave fornecida pela disciplina (apenas em `.env` ou variável de ambiente) |
| `MINICODE_MODEL` | nome do modelo servido pelo endpoint (um Qwen de ~14B) |
| `MINICODE_DEBUG` | `1` grava o fluxo completo em `.minicode/debug.jsonl` (opcional) |
| `MINICODE_PLAN_API_BASE`, `MINICODE_PLAN_MODEL` | (Parte 2, opcionais) URL e nome de um **modelo especializado** que escreve a primeira versão do plano de testes; `MINICODE_PLAN_API_KEY` é opcional. Sem elas, um modelo só faz tudo |
| `MINICODE_ABLACAO` | (executores de `eval_tasks/`, opcional) liga ou desliga componentes do agente, por exemplo `planejar_testes=False` |
| `MINICODE_PAUSA` | (executores, opcional) segundos de pausa entre chamadas; padrão 1, use 0 em servidor próprio |

Uso: entre na pasta do projeto que será modificado e rode `minicode`.

```bash
cd meu_projeto
minicode
> Crie em fatorial.py a função fatorial(n); levante ValueError se n < 0.
```

O comando usa a pasta atual como projeto e fica em modo interativo: dá para pedir várias tarefas na mesma sessão. Também aceita uma tarefa só (`minicode "pedido"`), que sai com código 0 se concluiu.

### Modo interativo

A tela mostra o que o agente faz, em tempo real:

```
━━ [1/5] Especificação ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  … escrevendo a especificação (2.1s)
  ▸ read_file calculadora.py  (6 linhas)
  ✓ revisão da especificação: aprovada
━━ [4/5] Implementação ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✦ Há um '+ 1' desnecessário no denominador. Vou corrigir isso.
  ✎ write_file calculadora.py  (+3 −1)
    -    return sum(valores) / (len(valores) + 1)
    +    return sum(valores) / len(valores)
━━ [5/5] Verificação ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ revisão do código: aprovada
  ✗ testes: 1 falhou, 2 passaram
━━ Reparo 1/3 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  culpado: TEST_BUG  (IMPLEMENTING (testes))
━━ Resultado ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ CONCLUÍDO
```

| Símbolo | Significado |
|---|---|
| `…` | chamada à LLM em andamento (com o tempo que levou) |
| `✦` | o "pensamento" que o modelo declarou para escolher a ação |
| `▸` / `✎` / `✗` | ferramenta de leitura / escrita (com diff) / ação negada pelo harness |
| `✓` / `✗` | verificação aprovada / reprovada |
| `⚑` | diagnóstico de uma falha |

Comandos: `/ajuda`, `/spec` (última especificação), `/plano` (plano e plano de testes), `/diff` (o que mudou nos arquivos que já existiam), `/log` (últimos eventos do rastro), `/sair`. `Ctrl+C` interrompe a tarefa em andamento sem fechar a sessão. Projetos de demonstração prontos: `python examples/preparar_demos.py <pasta>` cria cinco (função nova, bug, vários arquivos, API, segurança), cada um com um repositório git.

## 2. Arquitetura em uma página

```
                      ┌────────────────────┐
   pedido ───────────▶│    ORCHESTRATOR    │  único que muda o estado
                      │ (máquina de estados│
                      │   + hard gates)    │
                      └─────┬────────┬─────┘
                            │        │
                  ┌─────────▼──┐  ┌──▼─────────────────────┐
                  │    LLM     │  │ HARNESS (código)       │
                  │ propõe JSON│  │ valida · executa ·     │
                  │ (schema)   │  │ restringe · registra   │
                  └────────────┘  └──┬─────────┬─────────┬─┘
                                     │         │         │
                                  tools/     safety/   tracing/
```

| Módulo (`src/minicode/`) | Responsabilidade |
|---|---|
| `agent/maquina/estados.py` | `Execucao`, tabela de transições e **hard gates** do estado |
| `agent/orquestrador.py` | a sequência do fluxo e o laço central (implementar → verificar → diagnosticar → reparar) |
| `agent/etapas/planejamento.py` | spec, plano e plano de testes |
| `agent/etapas/verificacao.py` | revisão do código, pytest e revisão dos testes, com o orçamento de veto |
| `agent/etapas/reparo.py` | diagnóstico, correção do plano, descarte final de testes e mensagens do reparo |
| `agent/maquina/controle.py` | base: mudar o estado (`avancar`), encerrar e funções comuns |
| `agent/conversas/fases.py` | laço de conversa com a LLM, execução de ações, fases de documento e de implementação |
| `agent/gates/escrita.py` | **hard gates de escrita** (teste protegido, restrição do diagnóstico, Python válido, não perder testes) |
| `agent/conversas/revisoes.py` | chamadas "juiz": revisões, plano de testes e diagnóstico |
| `llm/` | cliente do endpoint, parser de ações, JSON Schema (`response_format`) |
| `spec/` | prompts, validação de documentos, esquemas e prompts das revisões/diagnóstico/plano de testes |
| `tools/` | ferramentas: arquivos, busca, `git diff`, execução do pytest |
| `safety/` | sandbox de caminhos, testes protegidos, validador de comandos |
| `tracing/` | rastreabilidade em `.minicode/`, modo de depuração e a **tela** do modo interativo (`tela.py`) |
| `cli/` | comando `minicode` |

## 3. Fluxo do agente

Cada seta é uma transição controlada pelo programa (`TRANSICOES` em `estados.py`); qualquer outra é proibida.

```
RECEIVED ─▶ SPECIFIED ─▶ PLANNED ─▶ TEST_PLANNED ─▶ IMPLEMENTING ─▶ VERIFYING ─▶ DONE
                            │                            ▲   ▲          │
                            └── (sem plano de testes) ───┘   │          ├─ pytest falhou ─▶ DIAGNOSING ─┐
                                                             │          └─ revisão reprovou ─┐           │
                                                             │                               ▼           ▼
                                                             └─────────────────────────── REPAIRING ◀─────┘
        qualquer estado ─▶ FAILED          DIAGNOSING ─▶ TEST_PLANNED ─▶ REPAIRING   (o diagnóstico apontou o plano de testes)
```

1. **SPECIFIED** – o pedido vira `specification.md` (Objective + Acceptance Criteria). Uma revisão confere a spec contra o pedido (até 2 reescritas).
2. **PLANNED** – a spec vira `plan.md`.
3. **TEST_PLANNED** – os casos de teste (critério, entrada, valor esperado) são definidos **antes do código**. O programa exige que todo critério tenha caso e uma revisão confere os valores.
4. **IMPLEMENTING** – a LLM lê, busca e escreve arquivos (JSON forçado por schema) e pede `finish`.
5. **VERIFYING** – três verificações em ordem: revisão do código contra a spec → **pytest rodado pelo programa** → revisão dos testes contra o plano.
6. **DIAGNOSING / REPAIRING** – falha de teste é classificada (`CODE_BUG`, `TEST_BUG`, `PLAN_BUG`, `ENVIRONMENT_ERROR`, `UNKNOWN`) e o reparo age sobre a etapa culpada (seção 7).
7. **DONE** só com testes passando; **FAILED** ao esgotar tentativas ou iterações.

## 4. Ferramentas

A LLM só enxerga as ferramentas permitidas no estado atual (o `enum` do schema é gerado de `FERRAMENTAS_POR_ESTADO`). Cada ferramenta recebe a raiz do projeto e devolve `(ok, texto)`; erros voltam à LLM como texto para ela corrigir.

| Ferramenta | Estados | O que faz |
|---|---|---|
| `list_files` | leitura e implementação | lista os arquivos do projeto (ignora `.git`, `.venv`, `__pycache__`, `.minicode`...) |
| `read_file` | leitura e implementação | lê um arquivo (cortado a 5 000 caracteres) |
| `search_code` | leitura e implementação | procura um trecho no projeto e devolve `arquivo:linha: trecho` |
| `git_diff` | implementação | mostra o que mudou desde o último commit |
| `create_file` | implementação | cria um arquivo **novo** (recusa se ele já existe) |
| `write_file` | implementação | sobrescreve um arquivo existente com o conteúdo completo |
| `finish` | implementação | pseudo-ferramenta: encerra a implementação (o gate decide se vale) |
| `run_tests` | **só o programa** | roda `pytest`; a LLM não tem acesso |

Separação explícita **LLM × sistema**: a LLM não executa nada, apenas escolhe uma ação; o programa valida e executa.

## 5. Spec-Driven Development

- O agente **não pode** implementar sem passar por `SPECIFIED` e `PLANNED` (transições e gates em `estados.py`).
- A spec precisa das seções `## Objective` e `## Acceptance Criteria` com no mínimo 2 critérios verificáveis (`spec/documentos.py`).
- Uma revisão compara a spec com o **pedido original** (requisito por requisito) e pode mandar reescrever.
- O plano de testes liga cada critério a casos concretos. O campo `criterio` do schema é um `enum` com os critérios reais da spec, então o modelo não pode citar um critério que não existe; o programa exige cobertura total.
- Todo o rastro fica em `.minicode/specification.md`, `plan.md` e `test_plan.md`.

## 6. Agent Hardness (hard gates)

Regras **impostas pelo código**, não pedidas no prompt:

| Gate | Onde | Efeito |
|---|---|---|
| Sem spec → não vai para `SPECIFIED`; sem plano → não vai para `PLANNED` | `estados.py` | impede pular etapas |
| Transições fora de `TRANSICOES` | `estados.py` | `TransicaoInvalida` |
| `VERIFYING` exige arquivo alterado e os arquivos citados no pedido no caminho exato | `estados.py` | `finish` recusado, com o motivo devolvido à LLM |
| `DONE` exige **testes passando** e, com revisão ligada, as duas revisões aprovadas | `estados.py` | o agente não declara sucesso com testes falhando |
| `REPAIRING` exige falha real e tentativas restantes (máx. 3) | `estados.py` | fim do laço de reparo |
| Ferramentas por estado (menor privilégio) | `estados.py` + schema | a ação fora do estado é impossível de gerar |
| Testes que já existiam não podem ser sobrescritos | `escrita.py` | proteção do oráculo |
| **Ler antes de sobrescrever:** gravar um arquivo que já existe exige tê-lo lido na conversa atual da implementação | `escrita.py` | evita reescrever "de memória" e apagar código existente (como o Claude Code) |
| Um teste que já existia **nunca é o culpado** de uma falha: o diagnóstico é corrigido para `CODE_BUG` | `reparo.py` | o oráculo confiável manda; a regressão é do código |
| Depois do diagnóstico, o reparo só altera o lado apontado (testes **ou** código) | `escrita.py` | evita "consertar" o lado errado |
| Python precisa compilar e não ter código inalcançável | `escrita.py` | escrita recusada antes de gravar |
| Sobrescrever um arquivo de teste não pode apagar testes | `escrita.py` | evita perder cobertura |
| O teste que falhou precisa **mudar** para ser regravado | `escrita.py` | acaba com a regravação idêntica |
| Limite de iterações (40), de leituras nas fases de documento (4) e recusa de chamada repetida | `estados.py`/`fases.py` | impede laços |
| Cada critério só pode ser reprovado uma vez por um juiz LLM | `verificacao.py` | um juiz é opinião, não oráculo; os testes decidem |
| Fim das tentativas com o diagnóstico apontando o teste: os testes **escritos pelo modelo** que continuam falhando são descartados e tudo é verificado de novo | `reparo.py` | testes que já existiam são o oráculo confiável; os do modelo, não. O `DONE` continua exigindo testes passando |

## 7. Repair loop

Quando a verificação falha, o erro volta ao modelo **com contexto**:

1. **Falha de teste** → `DIAGNOSING`: uma chamada independente (contexto limpo) classifica a falha e cita um trecho **verdadeiro** da spec (se a citação não existir na spec, o diagnóstico é rebaixado para `UNKNOWN`).
2. A classificação define a **etapa culpada** e a ação:

   | Diagnóstico | Etapa | Ação do programa |
   |---|---|---|
   | `CODE_BUG` | código | só arquivos de código podem mudar |
   | `TEST_BUG` | teste | o programa **remove** o teste errado (para o modelo não copiá-lo de volta) e a conversa recomeça |
   | `PLAN_BUG` | plano de testes | `DIAGNOSING → TEST_PLANNED`: o plano é corrigido com a evidência e só então o teste é refeito |
   | `ENVIRONMENT_ERROR` / `UNKNOWN` | indefinida | reparo sem restrição de arquivos |

3. **Escalonamento:** se o teste é reescrito e a falha volta idêntica (comparada pela *assinatura* das linhas de erro do pytest), `TEST_BUG` sobe para `PLAN_BUG`.
4. O reparo mostra o **diff** contra o original dos arquivos que já existiam, para o modelo ver o que mudou.
5. Falha de **revisão** vai direto a `REPAIRING` com o relatório.
6. Cada reparo grava um evento `reparo` em `actions.jsonl` com motivo, culpado, etapa, ação e tentativa.
7. **Hierarquia de confiança:** se as tentativas acabam e o diagnóstico aponta o teste (não o código), o programa descarta os testes escritos pelo modelo que continuam falhando, revisa o código de novo e roda o pytest. Testes que já existiam no projeto nunca são descartados. O descarte aparece no resultado final e no evento `testes_descartados`. Motivo: em 7 de 16 execuções que terminaram `FAILED`, o código em disco estava correto no verificador oculto; quem falhava eram os testes do próprio modelo.
8. Os juízes (revisões e diagnóstico) recebem o **pedido original** além da spec; se os dois divergirem, vale o pedido.

## 8. Segurança

- **Sandbox de caminhos** (`safety/caminhos.py`): todo caminho é resolvido e recusado se sair do projeto (`..`, links).
- **A LLM não executa comandos.** As únicas execuções de processo são `pytest` (rodado pelo programa, com tempo limite) e `git diff` (argumentos fixos). Princípio do menor privilégio: o dano possível é a união das ferramentas de escrita, que são só `create_file` e `write_file` dentro do projeto.
- **Segredos:** o `pytest` executa código escrito pelo modelo, por isso recebe apenas variáveis de ambiente de uma lista de permitidas; `MINICODE_API_KEY` não chega a ele.
- **Validador de comandos** (`safety/comandos.py`): bloqueia `sudo`, `shutdown`, `reboot`, `poweroff`, `halt`, `mkfs`, `dd`, `format` e `rm -r` em alvos perigosos. Está implementado e testado, mas **não há ferramenta que execute comandos escolhidos pela LLM**; ele fica pronto para uma futura `run_command`.
- **Limites:** iterações, leituras, tentativas de reparo, tempo do `pytest` (120 s) e do cliente (60 s).
- **Limitação conhecida:** o `pytest` roda código gerado no próprio computador, sem container.

## 9. Rastreabilidade

Cada execução grava em `.minicode/` (ignorado pelo git):

| Arquivo | Conteúdo |
|---|---|
| `specification.md`, `plan.md`, `test_plan.md` | os documentos produzidos |
| `actions.jsonl` | uma linha por evento: chamada à LLM, ferramenta, mudança de estado, testes, revisão, diagnóstico, reparo, resultado final |
| `state.json` | estado atual, tentativas, iterações, chamadas, arquivos alterados |
| `debug.jsonl` | (opcional, `MINICODE_DEBUG=1`) prompts e respostas completos |

Dá para reconstruir: a tarefa, a spec, o plano, as ferramentas chamadas, os arquivos alterados, os testes e erros, as tentativas e o resultado.

## 10. Avaliação e resultados

Duas baterias com **verificadores ocultos** (testes que o agente nunca vê): 15 tarefas fáceis e 10 difíceis, de seis tipos (função, bug, API, criação de testes, validação, refatoração). Métricas: **TaskSuccessRate**, **FirstAttemptSuccess**, **AverageIterations**, **AverageLLMCalls**. Como rodar e como cada tarefa é verificada: [eval_tasks/README.md](eval_tasks/README.md).

Modelo: `qwen2.5:14b` (Ollama), em todas as medições.

### Conjunto difícil (10 tarefas)

Execução final (commit `4ab8031`), modelo `qwen2.5:14b`:

| Métrica | Valor |
|---|---|
| **TaskSuccessRate** | **9/10 = 90 %** |
| **FirstAttemptSuccess** | 4/10 = 40 % |
| **AverageIterations** | 22,5 |
| **AverageLLMCalls** | 22,5 |
| Tarefas que chegaram a `DONE` | 10/10 (nenhuma terminou `FAILED`) |
| Tempo médio por tarefa | 69 s |

A única tarefa incorreta foi `contar linhas e palavras`: o plano de testes descreveu o retorno como texto onde o pedido pedia lista, e o código e o teste foram escritos sobre esse erro (detalhes na seção 11).

Evolução do sistema nesse conjunto (uma execução por linha, exceto onde indicado; o ruído entre execuções idênticas é de cerca de ±20 pontos):

| Versão | TaskSuccess |
|---|---|
| prompts com regras específicas, sem reparo estruturado | 53 %, 53 %, 57 % |
| prompts gerais, schema JSON, revisões e diagnóstico | 60 % |
| + plano de testes, reparo em 3 níveis (código, teste, plano), orçamento de veto | 60 %, 70 %, 70 % |
| + ler antes de sobrescrever, teste do projeto nunca é o culpado, descarte final de testes | **90 %** |

A melhora de 67 % (média das três execuções anteriores) para 90 % é consistente com os mecanismos adicionados: o `remover usuário`, que falhava por reescrever arquivos às cegas, passou sem nenhum reparo, e o `arredondar_moeda` e o `validar_senha`, que travavam por testes errados, também fecharam. Mesmo assim é **uma execução**, e as tarefas foram usadas para desenvolver o agente, então o número é otimista.

### Repetição depois da refatoração do orquestrador

Depois de dividir o orquestrador em módulos (sem mudar comportamento), os dois conjuntos foram rodados de novo para conferir que não houve regressão:

| Conjunto | Execução final | Repetição | Média das duas |
|---|---|---|---|
| Difícil (10) | 90 % (9/10) | 80 % (8/10) | 85 % |
| Fácil (15) | 87 % (13/15) | 93 % (14/15) | 90 % |

Na repetição: difícil com FirstAttempt de 40 % e 20,7 chamadas por tarefa; fácil com FirstAttempt de 53 % e 17,9 chamadas por tarefa. Nenhuma execução terminou com erro de programa (traceback). A queda de FirstAttempt no conjunto fácil (73 % para 53 %) é de 3 tarefas e está dentro da variação entre execuções, mas não dá para garantir que seja só isso com uma execução por conjunto.

Uma segunda execução com uma checagem de tipo no plano de testes (descrita abaixo, em "O que não funcionou") deu 60 %, e a checagem foi descartada. A variação entre 90 % e 60 % entre duas execuções quase iguais é uma medida direta do ruído desse conjunto de 10 tarefas.

### Conjunto fácil (15 tarefas)

Execução final (commit `4ab8031`), mesmo modelo:

| Métrica | Valor |
|---|---|
| **TaskSuccessRate** | **13/15 = 87 %** |
| **FirstAttemptSuccess** | 11/15 = 73 % |
| **AverageIterations** / **AverageLLMCalls** | 16,6 / 16,6 |
| Tarefas que chegaram a `DONE` | 14/15 |
| Tempo médio por tarefa | 40 s |

Por tipo: implementar 4/4, bug 3/3, API 2/2, refatorar 2/2, validação 1/2, criar testes 1/2.

As duas incorretas:
- `testes de primo` (criar testes): o agente chegou a `DONE`, mas criou só 2 funções de teste e o verificador exige mais.
- `validar_email` (validação): o código aceitava um domínio sem ponto e o agente não conseguiu corrigir em 3 reparos; o diagnóstico oscilou entre `TEST_BUG` e `CODE_BUG`.

Nas execuções durante o desenvolvimento esse conjunto tinha dado 93–100 %; a diferença é de uma ou duas tarefas, dentro do ruído de uma execução só, mas não dá para excluir que algum gate novo tenha custado uma tarefa.

**Ressalva importante:** as 10 tarefas difíceis foram usadas durante o desenvolvimento para encontrar falhas, portanto a taxa nelas é otimista. A generalização deve ser lida nas tarefas inéditas.

### O que não funcionou (e foi removido)
Resultados negativos fazem parte da resposta experimental:

| Tentativa | Resultado |
|---|---|
| `replace_text` (opcional e obrigatório no reparo) | o 14B erra o trecho `old`; 0/3 no início da rodada com ele obrigatório |
| Temperatura crescente no reparo | 30/30 regravações idênticas a 0,3, 0,5 e 0,7; a temperatura não destrava a cópia |
| Varredura de temperatura | sem diferença distinguível do ruído (n pequeno); ficou o valor fixo por fase |
| `run_command` (comando da LLM validado por `safety/comandos.py`, com gate que desfaz gravações) | funcionou e recusou caminhos fora do projeto, mas na demo de correção de bug o 14B o usou 5 a 8 vezes por execução, quase sempre para rodar o `pytest` que o sistema já roda, e consumiu as 40 iterações (1 de 2 execuções falhou; a versão anterior também falhou 1 de 3, amostra pequena). Retirado; o validador continua testado e disponível |
| Modelo de 7B | ~48 % no conjunto difícil; descartado |
| Prompts com exemplos de tarefas | induziam viés; foram trocados por regras gerais |
| Checagem de tipo no plano de testes (o juiz identifica o tipo que o critério pede e o que o caso descreve, e o programa compara) | detectou o erro do `contar linhas`, mas a tarefa terminou incorreta do mesmo jeito; gerou falso positivo (o número `5` descrito em prosa contou como texto); a execução seguinte deu 60 % contra 90 %. Descartada |

## 11. Limitações e honestidade

- O 14B comete erro **correlacionado**: é autor da spec, do plano, do código e dos testes, e também o juiz. Se ele lê errado uma frase ambígua do pedido, todas as camadas herdam o erro (ex.: devolver `str` onde o pedido pede `list`).
- Juízes LLM erram nos dois sentidos (aprovam o errado e reprovam o certo). Por isso nenhum juiz bloqueia sozinho: os testes são o oráculo final.
- O modelo erra aritmética ao calcular valores esperados; a execução dos testes é quem corrige o plano (`PLAN_BUG`).
- O descarte final de testes favorece entregar código funcionando em vez de cobertura: um teste certo pode ser descartado se o diagnóstico errar. Fica registrado e é mostrado ao usuário.
- As limitações da Parte 2 (dataset sintético pequeno, 25 tarefas reais, ruído entre rodadas) estão na [seção 12](#12-parte-2-especializando-uma-llm).

## 12. Parte 2: especializando uma LLM

**Pergunta:** é possível especializar uma LLM pequena para executar melhor uma função do agente? **Função escolhida: escrever o plano de testes.** Na Parte 1, o Qwen-14B escreveu o valor esperado errado em 38% dos casos avaliáveis, e esses erros se propagam: o agente "conserta" um código que estava certo. A hipótese, os critérios de decisão e os limites foram escritos **antes** do treino em [docs/hipotese_parte2.md](docs/hipotese_parte2.md).

### Dataset ([datasets/plano_de_testes/](datasets/plano_de_testes/))
Cada exemplo é o prompt que o agente manda (pedido, spec e plano) e a resposta certa, um JSON `{"casos": [{criterio, entrada, esperado}]}`. O valor `esperado` **vem da execução da solução de referência, nunca de um modelo**. Modelos grandes (Nemotron 550B e 120B, DeepSeek v4.1) escrevem exercícios completos; o programa executa a referência, aplica filtros automáticos, um segundo modelo resolve o exercício só pelo pedido e as divergências são conferidas, e todos os exemplos foram lidos. **754 treino, 79 validação, 80 teste**, divididos por exercício. Detalhes, processo e limitações no [README do dataset](datasets/plano_de_testes/README.md).

### Modelo e LoRA
Qwen2.5-1.5B-Instruct com LoRA: o peso `W` fica congelado e aprendemos só `ΔW = B·A`, com `A ∈ ℝ^(r×d)`, `B ∈ ℝ^(d×r)` e `r ≪ d`, de modo que `W' = W + (α/r)·B·A`. `B` começa em zero, então o modelo parte idêntico ao original, e em vez de `d×d` parâmetros por matriz treinamos `2·r·d`. Com r=16 e α=32 nas 7 projeções de cada camada, são **18,46 milhões de parâmetros treináveis de 1,56 bilhão (1,18%)**, o que cabe numa GPU L4 do Colab. A perda é calculada só na resposta. 3 épocas (285 passos) em ~25 min.

Notebook (Colab, L4): [`notebooks/train_checkpoints.ipynb`](notebooks/train_checkpoints.ipynb). Ele treina 3 épocas, salva um adaptador por época e volta ao ponto de menor perda de validação. O adaptador de 3 épocas avaliado no Nível 1 veio de uma execução anterior do mesmo treino, sem os checkpoints (mesmos dados, semente e hiperparâmetros); aqui ele corresponde ao `adaptador_epoca3`, e o do melhor ponto é o `adaptador`. A avaliação não é feita no notebook: está em `experiments/`. Curvas em [`experiments/resultados/treino/`](experiments/resultados/treino/): a perda de validação para de cair por volta do passo 175 (0,140) e sobe um pouco (0,154), ou seja, **sobreajuste leve na terceira época**.

### Nível 1: a função sozinha
Os mesmos 60 prompts reais das 25 tarefas e 80 do teste sintético, para todos os modelos, com o formato forçado por JSON Schema (como o agente faz) e temperatura 0,3. Cada caso é executado na solução de referência (o **oráculo**): correto, errado ou inavaliável. Métrica: casos corretos ÷ (corretos + errados).

| Modelo | Real (25 tarefas) | Sintético (80 exercícios) |
|---|---|---|
| 1,5B base (baseline) | 10,2% | 9,2% |
| 1,5B base com 2 exemplos no prompt | 32,1% | 47,6% |
| **1,5B + LoRA (3 épocas)** | **65,0%** | **66,8%** |
| 1,5B + LoRA (melhor ponto da validação) | 67,5% | 71,5% |
| Qwen-14B (referência) | 67,4% | 69,8% |

Intervalos de confiança (bootstrap sobre tarefas) e comparações pareadas em [`experiments/resultados/nivel1/analise.md`](experiments/resultados/nivel1/analise.md). O ajustado supera o base e o base com 2 exemplos com intervalo separado de zero nos dois testes (**H1 confirmada**: passa do critério de +15 pontos definido antes). Contra o 14B, o resultado é **comparável**: as diferenças ficam dentro do ruído.

**Casos inavaliáveis.** O 14B escreve muitos casos que a referência nem consegue executar (65 no real, contra 18 do ajustado). Li os 355 casos inavaliáveis de 3 modelos um por um ([auditoria](experiments/resultados/nivel1/auditoria_inavaliaveis/)): 331 são testes quebrados pelo próprio modelo (objeto nunca criado, método chamado como função, texto no lugar de código), 14 eram testes válidos e corretos que o oráculo deixa de contar, e 10 dependem de arquivos. Contando os quebrados como erro, a nota do ajustado quase não muda (64,3% real, 65,1% sintético) e a do 14B cai (51,7% e 60,5%). A nota oficial é a pré-definida; esta é uma análise de sensibilidade.

**Limitações do Nível 1.** Só 25 tarefas reais, intervalos largos; o oráculo é tão bom quanto a referência (no teste sintético, li os 80 exercícios um a um: nenhuma referência contradiz o pedido e 7 têm ambiguidade, que muda os números em no máximo 2 pontos, ver [auditoria](experiments/resultados/nivel1/auditoria_referencias_teste/README.md); no teste real as referências passam nos verificadores ocultos); o 14B foi medido com o prompt cru, sem a revisão do plano que o agente faz; e nos planos em que **todos** os casos estão certos o 14B vai melhor (33% contra 20% no real).

### Nível 2: o agente completo e a ablação
O MiniCode aceita um modelo especializado só para a **primeira versão do plano de testes** (`MINICODE_PLAN_API_BASE` e `MINICODE_PLAN_MODEL`); a revisão e a correção do plano, a spec, o código e o reparo continuam no 14B. Três configurações nas 25 tarefas, com o verificador oculto de cada uma como régua:

- **A:** Qwen-14B sozinho (linha de base)
- **B:** 14B + 1,5B ajustado escrevendo o plano de testes
- **C:** sem a etapa do plano de testes (**ablação**)

| Configuração | Fáceis (15) | Difíceis (10) | Total (25), IC 95% |
|---|---|---|---|
| A: 14B sozinho | 15 | 7 | **22 (88%)**, IC 72 a 100 |
| B: 14B + 1,5B treinado | 12 | 6 | **18 (72%)**, IC 52 a 88 |
| C: sem plano de testes | 14 | 7 | **21 (84%)**, IC 68 a 96 |

Uma execução por configuração, 75 execuções no total, sem nenhum erro de infraestrutura (detalhes e por tipo de tarefa em [`experiments/resultados/nivel2/`](experiments/resultados/nivel2/)).

- **O híbrido ficou abaixo do 14B sozinho:** B − A = **−16 pontos** (IC 95% pareado por tarefa: −32 a −4, o intervalo não contém zero). O ganho do Nível 1 **não** virou ganho no agente.
- **A ablação:** sem o plano de testes (C) o agente acertou 4 pontos a menos que o A (IC −16 a +8, contém zero). Com o 14B, essa etapa contribui pouco.
- **O que os planos mostram** (o plano final gravado em cada execução, pontuado pelo oráculo): os planos do B tinham mais valores errados (64,6% corretos contra 77,9% no A; 8 de 25 planos sem nenhum erro contra 16 de 25), e o B precisou de mais voltas (23,4 contra 17,6) e acertou de primeira menos vezes (44% contra 64%). **Mas o plano não explica tudo:** 3 das 8 tarefas do B com plano sem erro também falharam, e o A falhou em 2 de 9 tarefas com plano errado. Um exemplo concreto está no `palíndromo` do B: o 1,5B esperou `True` para uma frase com vírgulas que a spec não cobre, o 14B reprovou o plano três vezes e o agente seguiu com ele até esgotar os reparos.
- **Ressalvas:** só uma execução por configuração (a Parte 1 mediu até 20 pontos de ruído entre rodadas) e os tempos por tarefa não são comparáveis, porque as três configurações rodaram juntas no mesmo servidor.

### Reproduzir
`pip install -e ".[dev]"`; o treino roda nos notebooks do Colab com a pasta `datasets/plano_de_testes/` (o notebook lê `exemplos_*.jsonl` e `entradas_reais.json`) e instala `peft` sozinho. A avaliação e a geração do dataset estão em [experiments/README.md](experiments/README.md). Os pesos dos adaptadores não estão no repositório.

## 13. Estrutura do repositório

```
src/minicode/   código do agente (agent, llm, spec, tools, safety, tracing, cli)
tests/          testes do MiniCode (não chamam a LLM)
examples/       projetos de demonstração para o modo interativo
eval_tasks/     tarefas de avaliação com verificadores ocultos e o executor
docs/           arquitetura detalhada
experiments/    Parte 2: oráculo, avaliação (Nível 1 e 2), pipeline do dataset, resultados (ver experiments/README.md)
datasets/       Parte 2: o dataset do plano de testes (754 / 79 / 80 exemplos)
notebooks/      Parte 2: treino LoRA no Colab (train_checkpoints.ipynb)
```

## 14. Uso de IA
Ver [AI_USAGE.md](AI_USAGE.md).

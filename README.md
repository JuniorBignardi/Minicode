# MiniCode

Agente de programação simplificado, inspirado no Claude Code, desenvolvido como trabalho da disciplina de Redes Neurais Artificiais (Parte 1). Dado um pedido em linguagem natural, o MiniCode lê o projeto, escreve uma **especificação** e um **plano**, define os **testes** antes do código, implementa, roda os testes e **repara** os erros, tudo sob controle de um harness programático.

A ideia central do trabalho: **a LLM propõe, o programa decide.** O modelo escolhe ações em JSON; quem valida, executa, restringe e registra é o código.

```
pedido ─▶ SPEC ─▶ PLANO ─▶ PLANO DE TESTES ─▶ IMPLEMENTAÇÃO ─▶ VERIFICAÇÃO ─▶ DONE
                                                   ▲               │ falhou
                                                   └── REPARO ◀── DIAGNÓSTICO
```

Documentação detalhada: [docs/architecture.md](docs/architecture.md) · avaliação: [eval_tasks/README.md](eval_tasks/README.md) · uso de IA: [AI_USAGE.md](AI_USAGE.md).

## 1. Como executar

Requisitos: Python 3.10+ e acesso a um endpoint OpenAI-compatível com um modelo Qwen (a disciplina fornece o de ~14B).

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows (PowerShell)

pip install -e ".[dev]"

cp .env.example .env               # preencha os valores; o .env nunca vai para o git
pytest                             # 300+ testes, sem chamar a LLM
```

| Variável | Descrição |
|---|---|
| `MINICODE_API_BASE` | URL base do endpoint OpenAI-compatível |
| `MINICODE_API_KEY` | chave fornecida pela disciplina (apenas em `.env` ou variável de ambiente) |
| `MINICODE_MODEL` | nome do modelo servido pelo endpoint (um Qwen de ~14B) |
| `MINICODE_DEBUG` | `1` grava o fluxo completo em `.minicode/debug.jsonl` (opcional) |

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
| `agent/estados.py` | `Execucao`, tabela de transições e **hard gates** do estado |
| `agent/orquestrador.py` | a sequência do fluxo e o laço central (implementar → verificar → diagnosticar → reparar) |
| `agent/planejamento.py` | spec, plano e plano de testes |
| `agent/verificacao.py` | revisão do código, pytest e revisão dos testes, com o orçamento de veto |
| `agent/reparo.py` | diagnóstico, correção do plano, descarte final de testes e mensagens do reparo |
| `agent/controle.py` | base: mudar o estado (`avancar`), encerrar e funções comuns |
| `agent/fases.py` | laço de conversa com a LLM, execução de ações, fases de documento e de implementação |
| `agent/escrita.py` | **hard gates de escrita** (teste protegido, restrição do diagnóstico, Python válido, não perder testes) |
| `agent/revisoes.py` | chamadas "juiz": revisões, plano de testes e diagnóstico |
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
| Modelo de 7B | ~48 % no conjunto difícil; descartado |
| Prompts com exemplos de tarefas | induziam viés; foram trocados por regras gerais |
| Checagem de tipo no plano de testes (o juiz identifica o tipo que o critério pede e o que o caso descreve, e o programa compara) | detectou o erro do `contar linhas`, mas a tarefa terminou incorreta do mesmo jeito; gerou falso positivo (o número `5` descrito em prosa contou como texto); a execução seguinte deu 60 % contra 90 %. Descartada |

## 11. Limitações e honestidade

- O 14B comete erro **correlacionado**: é autor da spec, do plano, do código e dos testes, e também o juiz. Se ele lê errado uma frase ambígua do pedido, todas as camadas herdam o erro (ex.: devolver `str` onde o pedido pede `list`).
- Juízes LLM erram nos dois sentidos (aprovam o errado e reprovam o certo). Por isso nenhum juiz bloqueia sozinho: os testes são o oráculo final.
- O modelo erra aritmética ao calcular valores esperados; a execução dos testes é quem corrige o plano (`PLAN_BUG`).
- O descarte final de testes favorece entregar código funcionando em vez de cobertura: um teste certo pode ser descartado se o diagnóstico errar. Fica registrado e é mostrado ao usuário.
- Parte 2 (LoRA/QLoRA, dataset, ablação do treinamento) ainda não foi feita.

## 12. Estrutura do repositório

```
src/minicode/   código do agente (agent, llm, spec, tools, safety, tracing, cli)
tests/          testes do MiniCode (não chamam a LLM)
examples/       projetos de demonstração para o modo interativo
eval_tasks/     tarefas de avaliação com verificadores ocultos e o executor
docs/           arquitetura detalhada
experiments/    (Parte 2)
datasets/       (Parte 2)
notebooks/      (Parte 2)
```

## 13. Uso de IA
Ver [AI_USAGE.md](AI_USAGE.md).

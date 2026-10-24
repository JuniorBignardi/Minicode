# MiniCode

Agente de programação simplificado, inspirado no Claude Code, desenvolvido como trabalho da disciplina de Redes Neurais Artificiais. Dado um pedido em linguagem natural, o MiniCode analisa um projeto, escreve uma especificação e um plano, modifica os arquivos, roda os testes e tenta corrigir os erros, tudo sob controle de um harness programático.

> **Status (Parte 1):** 🚧 em desenvolvimento. Seções marcadas com 🚧 serão preenchidas junto com a implementação de cada módulo.

## 1. Arquitetura

```
        +------+
        | USER |
        +--+---+
           |
           v
   +--------------+      +-----+
   | ORCHESTRATOR |<---->| LLM |
   | (state       |      +-----+
   |  machine +   |
   |  hard gates) |
   +------+-------+
          |
   +------+--------+----------+
   |               |          |
   v               v          v
 tools/         safety/    tracing/
 (arquivos,     (valida    (.minicode/)
  testes)       ações)
```

A LLM só *propõe* ações. Quem executa, valida e registra é o programa.

| Módulo (`src/minicode/`) | Responsabilidade |
|---|---|
| `agent/` | Orquestrador, máquina de estados, hard gates e repair loop |
| `llm/` | Cliente do endpoint OpenAI-compatível, parsing da saída e LLM falso para testes |
| `tools/` | Ferramentas expostas ao agente |
| `spec/` | Geração e validação de `specification.md` e `plan.md` |
| `safety/` | Validação de comandos e de caminhos |
| `tracing/` | Escrita dos artefatos em `.minicode/` |
| `evaluator/` | Execução das tarefas de avaliação e métricas |
| `cli/` | Comando `minicode` |

## 2. Fluxo do agente 🚧

```
RECEIVED -> SPECIFIED -> PLANNED -> IMPLEMENTING -> VERIFYING -> DONE
                                         ^              |
                                         |              v (testes falham)
                                         +---------- REPAIRING
                                                        |
                                                        v (limite de tentativas)
                                                      FAILED
```

Tabela de transições e condições: ver [docs/architecture.md](docs/architecture.md).

## 3. Ferramentas 🚧

| Ferramenta | Descrição | Status |
|---|---|---|
| `list_files` | Lista arquivos do projeto | 🚧 |
| `read_file` | Lê um arquivo | 🚧 |
| `write_file` | Escreve/cria um arquivo | 🚧 |
| `run_tests` | Executa os testes do projeto | 🚧 |

## 4. Spec-Driven Development 🚧
Antes de qualquer implementação o agente transforma o pedido em uma especificação com critérios de aceitação verificáveis e, em seguida, em um plano.

## 5. Agent Hardness (hard gates) 🚧
Regras impostas pelo código, e não apenas pedidas no prompt. Exemplos planejados: sem spec não se implementa, sem plano não se implementa, e sem testes executados e passando não se chega a `DONE`.

## 6. Segurança 🚧
Validação de comandos (bloqueio de `sudo`, `rm -rf /`, `shutdown`, `reboot` etc.), escrita restrita ao diretório do projeto e limite de iterações.

## 7. Repair loop 🚧
Quando os testes falham, o erro e o contexto voltam à LLM para um novo patch, até passar ou atingir o máximo de tentativas.

## 8. Rastreabilidade 🚧
Cada execução grava em `.minicode/`: `specification.md`, `plan.md`, `actions.jsonl` e `state.json`.

## 9. Como executar

Requisitos: Python 3.10+.

```bash
# criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows (PowerShell)

# instalar
pip install -e ".[dev]"

# configurar credenciais (nunca commitar o .env)
cp .env.example .env               # e preencher os valores
```

Variáveis de ambiente usadas:

| Variável | Descrição |
|---|---|
| `MINICODE_API_BASE` | URL base do endpoint OpenAI-compatível |
| `MINICODE_API_KEY` | Chave de acesso fornecida pela disciplina |
| `MINICODE_MODEL` | Nome do modelo |

Uso e testes:

```bash
minicode          # 🚧 ainda não implementado
pytest
```

## 10. Avaliação 🚧
Conjunto de tarefas pequenas em `eval_tasks/`, com sucesso decidido por testes automatizados. Métricas: TaskSuccessRate, FirstAttemptSuccess, AverageIterations e AverageLLMCalls.

## 11. Estrutura do repositório

```
src/minicode/   código do agente
tests/          testes do MiniCode
eval_tasks/     tarefas de avaliação do agente
docs/           documentação de arquitetura
experiments/    (Parte 2)
datasets/       (Parte 2)
notebooks/      (Parte 2)
```

## 12. Uso de IA
Ver [AI_USAGE.md](AI_USAGE.md).

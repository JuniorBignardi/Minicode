# Uso de IA no desenvolvimento

Trabalho individual. Este documento descreve, de forma resumida, como ferramentas de inteligência artificial foram utilizadas durante o desenvolvimento do MiniCode.

## Ferramentas utilizadas
- **Claude Code** (extensão do VS Code), empregado principalmente em modo de planejamento.

## Forma de utilização
O enunciado permite e incentiva o uso de IA, desde que o aluno seja responsável pelo código e consiga explicá-lo. Por isso, o desenvolvimento é feito em conjunto com o Claude Code, com a seguinte divisão:

- **Planejamento:** discussão da arquitetura, das funcionalidades de cada módulo e das decisões de projeto antes da implementação.
- **Geração de ideias:** levantamento de alternativas de implementação, de casos de teste e de pontos de atenção.
- **Código:** procuro escrever os módulos de lógica do agente por conta própria (máquina de estados, hard gates, segurança, ferramentas e repair loop). O Claude Code ajuda a corrigir trechos e cria um código base quando tenho dificuldade, e esse código é revisado, ajustado e testado por mim. Peças mais mecânicas (por exemplo, estrutura inicial e arquivos de configuração) podem ter sido geradas em maior parte pela IA.
- **Regra de aceitação:** só incorporo ao projeto código que consigo explicar. Quando não entendo um trecho, peço explicação antes de seguir.

A proporção real entre código escrito por mim e código gerado pela IA em cada módulo é registrada na tabela abaixo, que é atualizada ao final de cada módulo.

As decisões de projeto, a integração entre os módulos e a validação dos resultados são de minha responsabilidade.

## Divisão de trabalho até o momento

| Etapa | Auxílio da IA | Atuação própria |
|---|---|---|
| Estrutura de pastas e `pyproject.toml` | criação da estrutura com base na sugerida no enunciado do trabalho | solicitação da inclusão dos módulos `safety/` e `tracing/` |
| README, `docs/architecture.md`, `.gitignore` e `.env.example` | elaboração dos esqueletos iniciais | revisão e preenchimento das seções conforme a implementação avança |
| `llm/client.py` (cliente do endpoint) | revisão do código | escrita do código: carregamento do `.env`, criação do cliente e função `chat` |
| `llm/parser.py` (extração da ação da resposta da LLM) | sugestões de melhoria: retornar `None` em vez de uma mensagem de erro, capturar `json.JSONDecodeError` em vez de `except` vazio, validar se o resultado é uma ação (dicionário com `tool` e `args`), proteger o `main()` com `if __name__ == "__main__"`, remover import não usado e alinhar os nomes das chaves ao protocolo | escrita da função com três tentativas de extração (JSON direto, remoção de blocos markdown, trecho entre chaves) |
| `tests/test_parser.py` | escrita dos casos de teste do parser | execução dos testes e correção do parser conforme as falhas |
| Módulos restantes (segurança, ferramentas, estados, repair loop) | _(a preencher conforme o desenvolvimento)_ | _(a preencher conforme o desenvolvimento)_ |

## Verificação
- Testes automatizados com `pytest`.
- Execuções do agente com o modelo fornecido pela disciplina.
- Leitura e explicação do código por mim.

## Pontos em que a IA errou ou foi necessário corrigir
_(a preencher durante o desenvolvimento, com exemplos concretos)_

## Credenciais
A chave de acesso ao endpoint é mantida apenas em `.env` ou em variáveis de ambiente, nunca no repositório (o arquivo `.env` está no `.gitignore`).

## Responsabilidade
Sou responsável por todo o código entregue e sou capaz de explicar a arquitetura, o código, os prompts, as ferramentas e os resultados.

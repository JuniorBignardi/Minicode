# Uso de IA no desenvolvimento

Trabalho individual. Este documento descreve, de forma resumida, como ferramentas de inteligência artificial foram utilizadas durante o desenvolvimento do MiniCode.

## Ferramentas utilizadas
- **Claude Code** (extensão do VS Code), empregado principalmente em modo de planejamento.
- **Modelos como professores na Parte 2** (geração dos exercícios do dataset): Nemotron 3 Ultra 550B e Nemotron 3.5 Super 120B (API da NVIDIA) e DeepSeek v4.1 Flash (Qwen cloud). Eles escrevem o exercício; **os valores esperados vêm da execução da referência pelo nosso programa, nunca de um modelo**.
- **Google Colab** (treino) e **RunPod** (servir o Qwen-14B e o 1,5B ajustado na avaliação do agente).

## Forma de utilização
O enunciado permite e incentiva o uso de IA, desde que o aluno seja responsável pelo código e consiga explicá-lo. Por isso, o desenvolvimento é feito em conjunto com o Claude Code, com a seguinte divisão:

- **Planejamento:** discussão da arquitetura, das funcionalidades de cada módulo e das decisões de projeto antes da implementação.
- **Geração de ideias:** levantamento de alternativas de implementação, de casos de teste e de pontos de atenção.
- **Código:** escrevi por conta própria o cliente da LLM e o parser de ações. A maior parte dos demais módulos (ferramentas, segurança, máquina de estados e gates, prompts, validação de documentos, tracing e fases do agente) foi escrita pelo Claude Code a partir de decisões de desenho tomadas por mim em modo de planejamento, e depois lida, executada e revisada por mim.
- **Testes:** os testes automatizados foram escritos principalmente pelo Claude Code, a partir dos comportamentos que defini; eu os executo e uso para conferir o código.
- **Regra de aceitação:** só incorporo ao projeto código que consigo explicar. Quando não entendo um trecho, peço explicação antes de seguir.

A divisão real entre código escrito por mim e código escrito pela IA em cada módulo é registrada na tabela abaixo, que é atualizada ao final de cada módulo.

As decisões de projeto, a integração entre os módulos e a validação dos resultados são de minha responsabilidade.

## Divisão de trabalho até o momento

| Etapa | Auxílio da IA | Atuação própria |
|---|---|---|
| Estrutura de pastas e `pyproject.toml` | criação da estrutura com base na sugerida no enunciado do trabalho | solicitação da inclusão dos módulos `safety/` e `tracing/` |
| README, `docs/architecture.md`, `.gitignore` e `.env.example` | elaboração dos esqueletos iniciais | revisão e preenchimento das seções conforme a implementação avança |
| `llm/client.py` (cliente do endpoint) | revisão do código | escrita do código: carregamento do `.env`, criação do cliente e função `chat` |
| `llm/parser.py` (extração da ação da resposta da LLM) | sugestões de melhoria: retornar `None` em vez de uma mensagem de erro, capturar `json.JSONDecodeError` em vez de `except` vazio, validar se o resultado é uma ação (dicionário com `tool` e `args`), proteger o `main()` com `if __name__ == "__main__"`, remover import não usado e alinhar os nomes das chaves ao protocolo | escrita da função com três tentativas de extração (JSON direto, remoção de blocos markdown, trecho entre chaves) |
| `tests/test_parser.py` | escrita dos casos de teste do parser | execução dos testes e correção do parser conforme as falhas |
| `safety/` (validação de caminhos e de comandos) e `tools/` (`list_files`, `read_file`, `write_file`, `run_tests`, registry) | escrita do código e dos testes | definição do contrato das ferramentas (`raiz` como primeiro argumento, retorno `(ok, texto)`, erros devolvidos como texto à LLM, `run_tests` sem testes conta como falha); leitura e execução dos testes |
| `agent/maquina/estados.py` (máquina de estados e hard gates) | escrita do código e dos testes | decisões de desenho: LLM pede `finish` e o programa roda os testes, 3 tentativas de reparo configuráveis, qualquer escrita invalida o resultado dos testes, `finish` sem escrita é recusado, escrita só em `IMPLEMENTING`; revisão |
| `spec/prompts.py`, `spec/documentos.py` | escrita do código e dos testes | decisões: documentos entre tags `<spec>`/`<plan>`, spec exige as seções `Objective` e `Acceptance Criteria` com no mínimo 2 critérios, histórico limpo por fase; revisão |
| `tracing/registro.py`, `agent/conversas/fases.py` | escrita do código e dos testes | decisões: orquestrador avança o estado, reparo continua a mesma conversa, `fases.py` importa o tracing, `args` obrigatório em toda ação; revisão |
| `agent/orquestrador.py`, `agent/conversas/fases.py`, `agent/gates/escrita.py`, `agent/conversas/revisoes.py`, `cli/main.py` | escrita do código e dos testes, e refatoração em módulos menores | decisões de desenho: duas revisões contra a spec (antes e depois dos testes), diagnóstico estruturado antes do reparo, remoção do teste errado, orçamento de veto dos juízes, contexto do reparo, ordem das verificações; leitura dos resultados dos benchmarks e escolha do que manter ou cortar |
| `spec/revisao.py`, `spec/diagnostico.py`, `spec/plano_de_testes.py` e o estado `TEST_PLANNED` | escrita do código e dos testes | decisão de criar uma etapa de definição dos testes antes do código; decisão de avaliar quem errou (código, teste ou plano) em vez de descartar o plano |
| `tools/` (`search_code`, `git_diff`, `create_file`, `replace_text` removido) | escrita do código e dos testes | escolha das ferramentas, decisão de retirar o `replace_text` e o `run_command` depois de medir |
| `tracing/tela.py`, `cli/main.py` (modo interativo), `examples/` | escrita do código e dos projetos de demonstração | pedido de mostrar mais ao usuário, como o Claude Code faz (etapas, pensamento do modelo, diff das escritas, resultado dos testes, reparos); escolha dos cenários de demonstração |
| `eval_tasks/` | escrita dos executores, das tarefas e dos verificadores ocultos | escolha dos tipos de tarefa, decisão de usar o Qwen 14B por um endpoint próprio, execução e interpretação das rodadas |
| `README.md`, `docs/architecture.md`, `eval_tasks/README.md` | redação | conferência dos números e das afirmações com os registros das execuções |
| Parte 2: hipótese e critérios (`docs/hipotese_parte2.md`) | redação | escolha da função (plano de testes), das hipóteses e dos limiares **antes** do treino |
| Parte 2: dataset (`experiments/dataset/`, `datasets/`) | código dos geradores, filtros, auditoria e leitura de todos os exemplos para achar e corrigir erros | decisão de usar o valor esperado vindo da execução da referência, de ficar com o dataset em vez de refazê-lo, de gerar mais exemplos em lotes de 10 revisados à mão, e de publicar o dataset |
| Parte 2: oráculo e avaliação (`experiments/gabarito/`, `experiments/nivel1/`, `experiments/nivel2/`) | código e testes | decisão de comparar todos os modelos com o mesmo prompt e o mesmo formato, de descartar as comparações sem schema, e de auditar os casos inavaliáveis |
| Parte 2: treino (`notebooks/train_checkpoints.ipynb`) | código dos notebooks | execução no Colab, escolha dos hiperparâmetros e leitura das curvas |
| Parte 2: integração (`llm/client.py`, `orquestrador.py`, `revisoes.py`) | código e testes do modelo especializado no plano de testes | decisão de usar o especialista só na primeira versão do plano, deixando a revisão e a correção no 14B |
| Parte 2: infraestrutura (RunPod) | a IA operou os servidores por SSH com a minha autorização (instalou Ollama e vLLM, copiou os adaptadores) | criação das contas e dos pods, recarga de crédito e desligamento dos pods |

## Verificação
- Testes automatizados com `pytest`.
- Execuções do agente com o modelo fornecido pela disciplina.
- Leitura e explicação do código por mim.

## Pontos em que a IA errou ou foi necessário corrigir
- **Regra de gate que criou um laço.** O gate "o teste que falhou precisa mudar" recusou a mesma escrita 20 vezes seguidas e consumiu as 40 iterações. Corrigido com um limite de recusas por reparo.
- **Afirmações sem medição.** A IA sugeriu que a temperatura crescente destravaria a regravação idêntica; o experimento controlado mostrou 30 de 30 repetições idênticas. Também sugeriu remover o `desescapar_conteudo` como obsoleto antes de olhar os dados (3 disparos em 293 execuções).
- **Correções que pioraram o sistema.** O `replace_text` obrigatório no reparo levou a 9 edições com sintaxe inválida numa tarefa; um prompt que dizia "os valores esperados já foram conferidos" fez o modelo confiar num valor errado. Ambos foram revertidos.
- **Melhoria que não se sustentou.** A IA propôs e implementou uma checagem de tipo no plano de testes para corrigir o `contar linhas`. A medição seguinte não mostrou ganho (a tarefa continuou incorreta), revelou um falso positivo e a taxa caiu de 90 % para 60 % (em parte ruído); a mudança foi revertida e registrada como resultado negativo.
- **Falhas de processo.** A IA editou o repositório enquanto um benchmark ainda iniciava processos e lançou um experimento paralelo contra o mesmo endpoint sem avisar, o que atrasou as chamadas do benchmark. Passou-se a rodar tudo em sequência.
- **Refatoração com defeito.** Ao agrupar os gates de escrita, uma versão quebrava quando a LLM mandava argumentos sem `path`; os testes automatizados pegaram.
- **Erros de verificação.** Um verificador oculto com expressão regular mal escapada reprovava tarefas corretas; foi corrigido e os verificadores passaram a ser conferidos contra uma solução de referência.
- **Falha de desenho que a IA não previu.** Ao isolar o contexto de cada fase, a conversa da implementação deixou de ver os arquivos lidos na fase de spec, e o agente sobrescrevia arquivos existentes sem tê-los visto (22% das sobrescritas). Só apareceu ao investigar uma falha concreta; a correção foi um gate de "ler antes de sobrescrever".
- **Ferramenta que o modelo usou mal.** A IA implementou o `run_command` ligado ao validador de comandos, com um gate que desfaz gravações feitas por comando. Em duas execuções da demo de correção de bug o modelo o usou 5 a 8 vezes, a maioria para rodar o `pytest` que o sistema já roda, e gastou as 40 iterações. Decidi retirá-lo e o commit foi revertido. A IA também rodou testes no endpoint errado (o `.env` apontava para outro modelo) sem conferir antes.
- **Escopo errado.** A IA incluiu um estudo de ablação na Parte 1, sendo que ele é da Parte 2; foi retirado do repositório e dos READMEs a pedido meu.
- **Viés em prompts.** Os primeiros prompts continham exemplos específicos das tarefas; a pedido meu foram trocados por regras gerais.

### Parte 2
- **Leitura que não foi leitura.** A IA disse ter lido todos os 687 exemplos de treino quando só tinha conferido uma versão compacta; só depois de eu pedir uma leitura de verdade (e ela achar cerca de 30 referências com valor esperado errado) o dataset foi corrigido.
- **Sugestão que contradizia uma decisão registrada.** A IA sugeriu publicar o dataset no GitHub, mas o próprio código dizia que os termos da API proibiam. Ela percebeu antes de publicar e perguntou; decidi que podia publicar.
- **Avaliação que media a coisa errada.** A primeira comparação foi feita sem forçar o formato JSON, e o modelo base tirou 0% porque não produzia um plano legível, e o 14B sem schema também não produziu nenhuma resposta legível. O agente real sempre usa schema. A IA parou o experimento, refez tudo com o mesmo schema para todos e o resultado antigo foi descartado, por ter medido o formato e não o conteúdo.
- **Métrica com definição errada.** Uma tabela de "planos sem nenhum caso errado" dava vantagem ao modelo base, porque os planos dele eram quase só casos que não rodam e passavam de graça. Foi percebido e corrigido na hora.
- **Casos inavaliáveis tratados como neutros.** A nota oficial deixava de fora os casos que a referência não executa. Ao ler os 355 casos, quase todos eram testes quebrados pelo próprio modelo (objeto nunca criado, texto no lugar de código), o que favorecia o 14B. A nota oficial foi mantida e a versão auditada entrou como análise de sensibilidade.
- **Comando perigoso sugerido.** A IA recomendou matar o processo do kernel antigo no Colab para liberar a GPU, e isso derrubou a sessão. Nada se perdeu porque os resultados e os adaptadores já estavam no Drive.
- **Erro de caminho no executor do Nível 2.** O teste de fumaça mostrou que os resultados foram gravados dentro de `eval_tasks/` por causa de um caminho relativo; a IA corrigiu e removeu a pasta criada por engano.
- **Estimativas de tempo erradas.** Previu 40 a 90 minutos para o treino (levou 25) e deu estimativas otimistas ou pessimistas para a geração e o envio dos arquivos.

## Credenciais
A chave de acesso ao endpoint é mantida apenas em `.env` ou em variáveis de ambiente, nunca no repositório (o arquivo `.env` está no `.gitignore`).

## Responsabilidade
Sou responsável por todo o código entregue e sou capaz de explicar a arquitetura, o código, os prompts, as ferramentas e os resultados.

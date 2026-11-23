"""Temas dos exercícios sintéticos.

O professor recebe um tema sorteado por chamada; quanto mais temas, menos exercícios repetidos.
"""

# os primeiros temas, gerais, usados nas primeiras rodadas
TEMAS_ORIGINAIS = [
    "manipulação de texto", "listas de números", "contagem em dicionários", "validação de dados de formulário",
    "cálculo de preços e descontos", "notas e médias de alunos", "estoque de uma loja (classe com estado)",
    "fila de atendimento (classe com estado)", "conversão de unidades", "formatação de números e textos",
    "ordenação com critério", "filtros em listas de dicionários",
    "leitura de uma linha de texto separada por vírgulas", "geometria básica", "sequências numéricas",
    "divisores e múltiplos", "datas representadas como tuplas (dia, mês, ano)", "senhas e nomes de usuário",
    "pontuação de um jogo", "horários representados como minutos", "contas bancárias (classe)",
    "agenda de contatos (classe)", "histórico de operações (classe com estado)", "códigos e identificadores",
    "porcentagens e juros", "tabelas de frete", "listas de tarefas", "temperaturas e clima", "cestas de compras",
]

# texto e strings
TEXTO = [
    "palíndromos e anagramas", "contagem de vogais e consoantes", "capitalização de nomes próprios",
    "abreviação de nomes e iniciais", "cifra de César", "compressão de texto por repetições (run-length)",
    "contagem de palavras e frases", "justificar texto em colunas", "formatação de CPF e telefone", "slugs de URL",
    "extração de hashtags e menções", "inversão de palavras e de frases", "truncar texto com reticências",
    "modelos de texto com campos entre chaves", "numerais romanos", "números por extenso até 99", "código Morse",
    "remoção de espaços e linhas duplicadas", "comparação de versões como 1.2.10",
    "partes de um caminho de arquivo escrito como texto", "formatação de valores em reais",
    "máscara de cartão de crédito", "separação de nomes CamelCase e snake_case", "cabeçalhos de e-mail simples",
    "contagem de letras maiúsculas e minúsculas", "busca de palavras em um texto",
    "substituição de palavras proibidas", "alinhamento de tabelas em texto", "contagem de caracteres especiais",
    "resumo de um texto pelas primeiras palavras",
]

# números e matemática
NUMEROS = [
    "números primos", "fatoração em primos", "máximo divisor comum e mínimo múltiplo comum",
    "variações da sequência de Fibonacci", "números perfeitos e amigos", "conversão entre bases numéricas",
    "soma e produto de dígitos", "raiz quadrada inteira e potências", "progressões aritméticas e geométricas",
    "triângulo de Pascal", "frações representadas por tuplas", "média ponderada", "mediana e moda",
    "desvio padrão simples", "arredondamento de valores", "variação percentual entre valores", "sequência de Collatz",
    "números de Armstrong", "troco com o menor número de moedas", "zeros no final de um fatorial", "números felizes",
    "interpolação linear", "escalonamento de valores para um intervalo", "contagem de dígitos de um número",
    "números triangulares e quadrados perfeitos", "paridade e alternância", "soma de múltiplos num intervalo",
    "somatórios com condição", "máximos e mínimos de uma sequência", "razão entre números consecutivos",
]

# listas, matrizes e estruturas de dados simples
LISTAS = [
    "remoção de duplicatas mantendo a ordem", "rotação de listas", "mesclagem de listas ordenadas", "busca binária",
    "partição de listas por critério", "achatamento de listas aninhadas", "janela deslizante sobre uma lista",
    "pares de números com soma alvo", "subsequência crescente mais longa", "agrupamento de itens por chave",
    "transposta de matrizes", "diagonais de uma matriz", "percurso em espiral de matrizes",
    "vencedor de uma partida de jogo da velha", "contagem de vizinhos num campo minado", "histograma em texto",
    "ranking com empates", "os N maiores elementos", "compressão de números consecutivos em intervalos",
    "interseção de intervalos", "união de intervalos sobrepostos", "paginação de listas",
    "ordenação estável por várias chaves", "máximo de cada grupo", "pilha (classe)", "fila circular (classe)",
    "conjuntos: união, interseção e diferença", "contagem de pares iguais", "elementos que aparecem uma única vez",
    "listas de listas e somas por linha",
]

# preços, impostos, estoque e outras regras de negócio
NEGOCIOS = [
    "juros compostos", "parcelas de um financiamento", "imposto de renda por faixas",
    "folha de pagamento e horas extras", "comissão de vendas por faixas", "cupons de desconto", "frete por distância",
    "nota fiscal com impostos", "conta de energia por faixas de consumo", "tarifa de táxi",
    "aluguel de carros por dias", "passagens com desconto por idade", "ingressos com meia-entrada",
    "assinatura mensal proporcional aos dias", "programa de fidelidade com pontos (classe)",
    "leilão com lances (classe)", "reposição de estoque mínimo", "inventário de um armazém (classe)",
    "caixa de supermercado (classe)", "extrato bancário com saldo", "limite de cartão de crédito (classe)",
    "câmbio entre moedas com tabela fixa", "orçamento mensal por categorias", "divisão de uma conta entre amigos",
    "gorjeta e taxa de serviço", "depreciação de bens", "ponto de equilíbrio de uma empresa",
    "preço com margem de lucro", "descontos progressivos por quantidade", "carteira de investimentos (classe)",
]

# jogos e simulações
JOGOS = [
    "placar de basquete", "pontuação de boliche", "jogo da forca (classe)", "verificação de tiros na batalha naval",
    "comparação de cartas de baralho", "movimentos do cavalo no xadrez", "caminho válido em um labirinto em grade",
    "robô em uma grade com comandos", "uma geração do jogo da vida", "pedra, papel e tesoura",
    "ranking de um torneio", "níveis e experiência de um personagem", "inventário de um jogo de RPG (classe)",
    "combate por turnos simples", "cartela de bingo", "validação de uma linha de sudoku",
    "mover uma linha do jogo 2048", "elevador (classe com estado)", "semáforo (classe com estado)",
    "máquina de refrigerante (classe)", "catraca de metrô (classe)", "pontuação de uma partida de dardos",
    "vencedor de uma rodada de dados", "sorteio determinístico por sequência dada", "jogo de adivinhação com dicas",
    "tabuleiro de damas: movimentos permitidos",
]

# datas e horários (representados como tuplas ou minutos, nunca o relógio de verdade)
TEMPO = [
    "dias em cada mês e anos bissextos", "diferença entre duas datas escritas como tuplas",
    "dia da semana de uma data", "idade em anos completos", "duração em horas e minutos", "formatação de durações",
    "conversão entre relógio de 12 e de 24 horas", "fusos horários por deslocamento em horas",
    "escala de turnos de trabalho", "agendamento de reuniões sem conflito", "calendário de reservas (classe)",
    "prazo de entrega em dias úteis", "contagem regressiva em segundos", "vencimentos de contas por mês",
    "relógio de ponto (classe)", "sobreposição de horários", "estação do ano de um mês", "signo por dia e mês",
    "feriados fixos em uma lista de datas", "semanas completas entre duas datas",
]

# validação de dados e de acesso
VALIDACAO = [
    "força de senhas", "validação de CPF", "validação de CNPJ", "dígito verificador pelo algoritmo de Luhn",
    "validação de ISBN", "validação de placas de carro", "validação de CEP", "validação de endereços IPv4",
    "cores em hexadecimal", "parênteses balanceados", "nome de arquivo seguro", "limites de idade em cadastros",
    "tentativas de login com bloqueio (classe)", "permissões por papel de usuário", "lista de bloqueio de palavras",
    "formulário de cadastro completo", "validação de e-mail", "validação de datas como tuplas",
    "validação de URLs simples", "tokens de sessão simulados com expiração (classe)",
]

# ciências, medidas e conversões
CIENCIAS = [
    "índice de massa corporal e faixas", "velocidade média e distância", "conversão de bytes (KB, MB, GB)",
    "distância entre pontos", "área e perímetro de polígonos", "volume de sólidos geométricos",
    "conversão entre graus e radianos", "consumo de energia de aparelhos", "concentração de soluções",
    "classificação de pH", "lei de Ohm e circuitos simples", "queda livre e movimento uniforme",
    "densidade e pressão", "notas musicais e frequências", "conversão de cores RGB e hexadecimal",
    "classificação de terremotos pela escala Richter", "calorias e nutrição", "dosagem de remédios por peso",
    "consumo de combustível", "equações de primeiro e segundo grau",
]

# escola, notas e cadastros
EDUCACAO = [
    "boletim com pesos e aprovação", "ranking de uma turma", "frequência e presença", "cadastro de alunos (classe)",
    "biblioteca com empréstimos (classe)", "horários de aulas sem conflito", "formação de grupos por regra",
    "bolsa de estudos por desempenho", "quiz com pontuação (classe)", "conceitos por faixas de nota",
    "classificação de um campeonato", "cadastro de funcionários (classe)", "organograma simples",
    "árvore genealógica simples", "lista de presença", "pontuação de currículos por critérios",
    "avaliação de desempenho com várias notas", "créditos de disciplinas e formatura",
    "inscrições em cursos com vagas (classe)", "plano de estudos por semana",
]

# dados em texto, dicionários e relatórios
DADOS = [
    "interpretação de CSV escrito em texto", "arquivos de configuração chave=valor",
    "parâmetros de uma consulta de URL", "linhas de log de um servidor", "estatísticas de logs por nível",
    "acessos por endereço IP", "mesclagem de dicionários", "dicionários aninhados achatados",
    "busca em dicionários aninhados", "diferenças entre dois dicionários", "versionamento de configurações (classe)",
    "cache com política LRU (classe)", "índice de palavras de um texto", "relatório em texto tabular",
    "ordenação de registros", "remoção de registros duplicados por chave", "vendas agrupadas por mês",
    "tabela com totais por linha e coluna", "contagem de eventos por categoria", "esquema de validação de registros",
]

# pequenos sistemas (classes com estado)
SISTEMAS = [
    "fila de impressão (classe)", "escalonador round-robin", "gerenciador de tarefas por prioridade (classe)",
    "desfazer e refazer (classe)", "editor de texto simples (classe)", "histórico de navegação (classe)",
    "carrinho de compras (classe)", "sistema de votação (classe)", "roteamento por prefixo de caminho",
    "limitador de requisições por contagem (classe)", "estacionamento com vagas (classe)",
    "reservas de um hotel (classe)", "pedidos de um restaurante (classe)", "entregas e rotas",
    "lista de reprodução de músicas (classe)", "fila de prioridade (classe)", "pool de recursos (classe)",
    "eventos e ouvintes (classe)", "máquina de estados de um pedido", "contador de visitas com limites (classe)",
]

# backend e plataformas: nada de rede, banco ou relógio de verdade; o tempo entra como parâmetro (por exemplo, "agora" em segundos)
BACKEND = [
    "limitador de requisições por janela de tempo (classe, o tempo entra como parâmetro)",
    "balde de fichas (token bucket) com o tempo como parâmetro", "cache com expiração por tempo (classe)",
    "repetição de tentativas com espera exponencial (só o cálculo das esperas)",
    "disjuntor de falhas (circuit breaker) com estados (classe)", "balanceador de carga round-robin (classe)",
    "balanceador pelo menor número de conexões (classe)", "hash consistente com md5 para escolher servidores",
    "verificação de saúde de serviços (health check) por contagem de falhas",
    "roteador de URLs com parâmetros como /usuarios/{id}", "análise de cabeçalhos HTTP",
    "negociação de conteúdo pelo cabeçalho Accept", "cookies: leitura e montagem do cabeçalho",
    "códigos de status HTTP e suas classes", "validação de um corpo JSON contra um esquema simples",
    "paginação por cursor", "paginação com links de próxima e anterior página",
    "ordenação e filtros vindos de parâmetros de consulta", "construtor de cláusulas WHERE com parâmetros",
    "repositório em memória com busca por campos (classe)",
    "exclusão lógica (soft delete) em um repositório (classe)", "restrições de unicidade em um repositório (classe)",
    "transações em memória com commit e rollback (classe)", "ordem de execução de migrações por dependências",
    "ordenação topológica de dependências entre serviços", "resolução de versões semânticas e intervalos",
    "fila de tarefas com tentativas e prioridade (classe)", "fila de mensagens com confirmação de entrega (classe)",
    "publicação e assinatura de tópicos (classe)", "eventos e reconstrução de estado a partir deles (event sourcing)",
    "chaves de idempotência para pedidos repetidos (classe)", "controle de acesso por papéis e permissões (RBAC)",
    "escopos de permissão de uma chave de API", "rotação de chaves de API com validade (classe)",
    "sessões de usuário com expiração (classe)", "bloqueio de contas após tentativas falhas (classe)",
    "assinatura de requisições com HMAC (hashlib e hmac)",
    "leitura das partes de um token no formato cabeçalho.corpo.assinatura em base64",
    "interruptores de funcionalidades (feature flags) por usuário",
    "sorteio de teste A/B determinístico a partir do id do usuário", "limites de cota de uso por plano (classe)",
    "faturamento por uso medido", "assinaturas: ativação, renovação e cancelamento (classe)",
    "livro-razão com partidas dobradas (classe)", "reembolsos parciais de pedidos",
    "estados de um pedido e transições permitidas", "reserva de estoque para pedidos (classe)",
    "carrinho com cupons e regras de desconto (classe)", "encurtador de URLs com base 62 (classe)",
    "geração de identificadores sequenciais no estilo snowflake a partir de parâmetros",
    "normalização de caminhos de URL e de arquivos", "tipos MIME por extensão de arquivo",
    "configuração em camadas: padrão, arquivo e variáveis de ambiente (como dicionários)",
    "mesclagem de configurações de vários ambientes", "análise de expressões cron simples (minuto e hora)",
    "agendador de tarefas periódicas com o tempo como parâmetro (classe)", "cálculo de percentis de latência",
    "agregação de métricas por minuto", "contadores e histogramas de métricas (classe)",
    "detecção de picos em séries de requisições", "auditoria: registro de quem fez o quê (classe)",
    "multi-inquilino: isolamento de dados por cliente (classe)", "notificações sem duplicatas (classe)",
    "fila de e-mails com limite por destinatário (classe)", "índice de busca invertido simples (classe)",
    "autocompletar com árvore de prefixos (classe)", "placar de líderes em tempo real (classe)",
    "agrupamento de eventos em sessões por intervalo de inatividade", "deduplicação de eventos por id e janela",
    "validação de webhooks: assinatura e idempotência", "serialização e desserialização de registros em texto",
    "exportação de registros para CSV em texto", "transformação de registros em etapas (ETL simples)",
    "mapeamento de erros internos para respostas HTTP", "versionamento de uma API por prefixo de rota",
    "limite de tamanho e tipo de arquivos enviados (validação de metadados)",
    "controle de concorrência otimista com números de versão (classe)",
    "reserva de salas ou recursos sem sobreposição (classe)",
    "sistema de comentários com respostas aninhadas (classe)", "votos e reputação de usuários (classe)",
    "relatório de uso por cliente e por mês",
]

# todos os temas juntos, sem repetição e na ordem em que aparecem acima
TEMAS = list(dict.fromkeys(
    TEMAS_ORIGINAIS + TEXTO + NUMEROS + LISTAS + NEGOCIOS + JOGOS + TEMPO
    + VALIDACAO + CIENCIAS + EDUCACAO + DADOS + SISTEMAS + BACKEND
))

"""Temas novos (v4) para gerar mais exercícios do plano de testes.

Critérios usados na escolha:
- áreas que o dataset v2 quase não cobre (grafos, árvores, programação dinâmica, estruturas de dados, física, biologia, jogos);
- resultado sempre determinístico e verificável por entrada e saída (sem aleatoriedade, data ou hora atuais);
- sem os temas em que o professor errou várias vezes (datas e dia da semana, dígito verificador/CPF/Luhn, signos,
  notas musicais, bases numéricas, MIME, CSV, resumo de texto) e sem empate de arredondamento em ponto flutuante.
"""

TEMAS_V4 = [
    # grafos e grades
    "contagem de ilhas em uma matriz de zeros e uns",
    "componentes conexos de um grafo não direcionado",
    "caminho de menor custo em um grafo pequeno com pesos inteiros",
    "campo minado: contar minas vizinhas de cada célula",
    "rotação de uma matriz quadrada em 90 graus",
    "busca de um valor em uma matriz com linhas e colunas ordenadas",
    "validação de um tabuleiro de sudoku completo (linhas, colunas e blocos)",
    # árvores e estruturas de dados
    "árvore binária de busca: inserir, buscar e percorrer em ordem",
    "altura e balanceamento de uma árvore binária guardada em tuplas aninhadas",
    "lista ligada simples implementada com classes",
    "heap mínimo implementado à mão",
    "tabela hash simples com encadeamento (classe com estado)",
    "pilha que informa o menor elemento a qualquer momento",
    "fila implementada com duas pilhas",
    "avaliação de expressão em notação pós-fixa",
    "calculadora de expressões com precedência de operadores",
    # programação dinâmica e algoritmos clássicos
    "mochila 0/1: maior valor possível dentro de um peso máximo",
    "distância de edição entre duas palavras",
    "maior subsequência comum entre duas palavras",
    "soma mínima de um caminho do topo à base de uma pirâmide de números",
    "número de maneiras de formar um valor com moedas dadas",
    "torre de Hanoi: número de movimentos e lista de movimentos para poucos discos",
    "ordenação por contagem de inteiros pequenos",
    "operações bit a bit: contar bits, potência de dois e máscaras",
    "triplas pitagóricas até um limite",
    # matemática e estatística
    "operações com polinômios guardados como listas de coeficientes",
    "operações com números complexos guardados como tuplas",
    "combinatória: fatorial, combinações e permutações",
    "quartis e amplitude interquartil de uma lista de inteiros",
    "regressão linear simples por mínimos quadrados com dados inteiros",
    "normalização de listas: mínimo-máximo e amplitude",
    "conversão de coordenadas cartesianas para polares com valores exatos",
    # ciência
    "movimento uniformemente variado: posição, velocidade e tempo",
    "massa molar de uma fórmula simples a partir de uma tabela de massas dada",
    "DNA: complemento reverso e contagem de bases",
    "tradução de códons para aminoácidos com uma tabela dada",
    "composição de uma mistura: fração de cada componente em porcentagem inteira",
    # jogos
    "jogo da forca: revelar as letras acertadas de uma palavra",
    "jogo da memória: conferir pares de cartas viradas",
    "pontuação de palavras no estilo Scrabble com uma tabela de valores dada",
    "cartas de truco simplificado: comparar duas cartas pela força dada",
    # serviços do dia a dia
    "caixa eletrônico: composição de cédulas para um saque",
    "estacionamento: cobrança por faixas de minutos de permanência",
    "locação de bicicletas: tarifa progressiva por minutos usados",
    "mapa de assentos de um cinema: reservar, liberar e contar lugares livres",
    "receita de culinária: ajustar as quantidades para outro número de porções",
    "temporizador de ciclos de trabalho e pausa: sequência de períodos em segundos",
    "quadro kanban: mover cartões entre colunas com limite de itens",
    "cartão fidelidade: acúmulo e troca de pontos por faixas",
    # texto
    "cifra de Vigenère com chave dada",
    "cifra de transposição por colunas",
    "quebra de um texto em linhas de largura fixa sem cortar palavras",
    "diferenças entre duas listas de linhas: acrescentadas, removidas e mantidas",
    "mesclagem de duas listas de eventos já ordenados por horário em minutos",
]

if __name__ == "__main__":
    print(len(TEMAS_V4), "temas;", len(set(TEMAS_V4)), "distintos")

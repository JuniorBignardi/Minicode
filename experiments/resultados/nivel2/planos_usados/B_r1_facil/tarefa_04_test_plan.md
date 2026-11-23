# Test Plan

1. Critério: A função `contar_palavras` deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são a contagem de ocorrências dessas palavras no texto.
   - entrada: contar_palavras('Olá mundo Olá outra vez')
   - esperado: {'ola': 2, 'mundo': 1, 'outra': 1, 'vez': 1}
2. Critério: A função deve ignorar a diferença entre maiúsculas e minúsculas, ou seja, "Palavra" e "palavra" devem ser consideradas a mesma palavra.
   - entrada: contar_palavras('Palavra palavra')
   - esperado: {'palavra': 2}
3. Critério: A função deve considerar que palavras são separadas por espaços.
   - entrada: contar_palavras('Vale mais vale')
   - esperado: {'vale': 2}
4. Critério: Teste a função com o texto "Python é uma linguagem de programação. Python é fácil de aprender." e verifique se o dicionário retornado contém os pares corretos de palavras e contagens.
   - entrada: contar_palavras('Python é uma linguagem de programação Python é fácil de aprender')
   - esperado: {'python': 2, 'é': 2, 'uma': 1, 'linguagem': 1, 'de': 1, 'programação': 1, 'fácil': 1, 'aprender': 1}
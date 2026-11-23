# Test Plan

1. Critério: A função `contar_palavras(texto)` deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são a contagem de ocorrências da palavra no texto.
   - entrada: contar_palavras('Olá mundo mundo')
   - esperado: { 'ola': 1, 'mundo': 2 }
2. Critério: A função `contar_palavras(texto)` deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são a contagem de ocorrências da palavra no texto.
   - entrada: contar_palavras('Teste de testes')
   - esperado: { 'teste': 2, 'de': 1 }
3. Critério: A função `contar_palavras(texto)` deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são a contagem de ocorrências da palavra no texto.
   - entrada: contar_palavras('')
   - esperado: {}
4. Critério: A função `contar_palavras(texto)` deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são a contagem de ocorrências da palavra no texto.
   - entrada: contar_palavras('Um dois dois três três três')
   - esperado: { 'um': 1, 'dois': 2, 'três': 3 }
5. Critério: A função deve ser testada com entradas como `"Olá mundo mundo"` e `"Teste de testes"` e retornar os resultados esperados `{ "ola": 1, "mundo": 2 }` e `{ "testes": 2, "de": 1 }` respectivamente.
   - entrada: contar_palavras('Olá mundo mundo')
   - esperado: { 'ola': 1, 'mundo': 2 }
6. Critério: A função deve ser testada com entradas como `"Olá mundo mundo"` e `"Teste de testes"` e retornar os resultados esperados `{ "ola": 1, "mundo": 2 }` e `{ "testes": 2, "de": 1 }` respectivamente.
   - entrada: contar_palavras('Teste de testes')
   - esperado: { 'testes': 2, 'de': 1 }
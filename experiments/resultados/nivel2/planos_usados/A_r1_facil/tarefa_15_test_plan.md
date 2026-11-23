# Test Plan

1. Critério: A função `maiusculas_lista` deve ser alterada para usar uma list comprehension.
   - entrada: maiusculas_lista([])
   - esperado: []
2. Critério: A função deve retornar uma lista com todos os elementos convertidos para maiúsculas.
   - entrada: maiusculas_lista(['ola', 'mundo'])
   - esperado: ['OLA', 'MUNDO']
3. Critério: A função deve funcionar corretamente com uma lista vazia.
   - entrada: maiusculas_lista([])
   - esperado: []
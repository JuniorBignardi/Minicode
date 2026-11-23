# Test Plan

1. Critério: A função `maiusculas_lista` deve ser substituída por uma única linha usando list comprehension.
   - entrada: maiusculas_lista(['abc', 'def'])
   - esperado: ['ABC', 'DEF']
2. Critério: A função refatorada deve retornar uma lista com cada elemento da lista de entrada convertido para maiúsculas.
   - entrada: maiusculas_lista(['abc', 'DEF'])
   - esperado: ['ABC', 'DEF']
3. Critério: A função refatorada deve retornar uma lista com cada elemento da lista de entrada convertido para maiúsculas.
   - entrada: maiusculas_lista(['abc', 123])
   - esperado: ['ABC', 123]
# Test Plan

1. Critério: A função `eh_palindromo` deve retornar `True` quando a string fornecida for um palíndromo, ignorando espaços e diferenciação de maiúsculas e minúsculas.
   - entrada: eh_palindromo('A man, a plan, a canal, Panama')
   - esperado: True
2. Critério: A função `eh_palindromo` deve retornar `True` quando a string fornecida for um palíndromo, ignorando espaços e diferenciação de maiúsculas e minúsculas.
   - entrada: eh_palindromo('Ovo')
   - esperado: True
3. Critério: A função `eh_palindromo` deve retornar `False` quando a string fornecida não for um palíndromo, mesmo quando espaços e diferenciação de maiúsculas e minúsculas são ignorados.
   - entrada: eh_palindromo('Abacaxi')
   - esperado: False
4. Critério: A função `eh_palindromo` deve retornar `False` quando a string fornecida não for um palíndromo, mesmo quando espaços e diferenciação de maiúsculas e minúsculas são ignorados.
   - entrada: eh_palindromo('Python')
   - esperado: False
5. Critério: A função `eh_palindromo` deve retornar `True` quando a string fornecida for um palíndromo, ignorando espaços e diferenciação de maiúsculas e minúsculas.
   - entrada: eh_palindromo('A Toyota na outra')
   - esperado: True
# Test Plan

1. Critério: A função `eh_palindromo` deve retornar `True` quando o texto fornecido for um palíndromo.
   - entrada: eh_palindromo('A man a plan a canal Panama')
   - esperado: True
2. Critério: A função `eh_palindromo` deve retornar `False` quando o texto fornecido não for um palíndromo.
   - entrada: eh_palindromo('Hello World')
   - esperado: False
3. Critério: A função `eh_palindromo` deve retornar `True` quando o texto fornecido for um palíndromo.
   - entrada: eh_palindromo('Was it a car or a cat I saw')
   - esperado: True
4. Critério: A função `eh_palindromo` deve retornar `False` quando o texto fornecido não for um palíndromo.
   - entrada: eh_palindromo('Python')
   - esperado: False
5. Critério: A função `eh_palindromo` deve retornar `True` quando o texto fornecido for um palíndromo.
   - entrada: eh_palindromo('Noon')
   - esperado: True
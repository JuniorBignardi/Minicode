# Test Plan

1. Critério: A função `saudacao` deve aceitar um parâmetro opcional `formal` com valor padrão `False`.
   - entrada: saudacao('João')
   - esperado: Olá, João
2. Critério: Quando `formal=True`, a função deve retornar 'Prezado(a) <nome>'.
   - entrada: saudacao('Maria', formal=True)
   - esperado: Prezado(a) Maria
3. Critério: Quando `formal=False` ou o parâmetro é omitido, a função deve retornar 'Olá, <nome>'.
   - entrada: saudacao('Carlos', formal=False)
   - esperado: Olá, Carlos
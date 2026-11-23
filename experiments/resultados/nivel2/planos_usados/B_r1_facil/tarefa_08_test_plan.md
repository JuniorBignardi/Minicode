# Test Plan

1. Critério: A função saudacao deve aceitar um segundo parâmetro opcional 'formal'.
   - entrada: saudacao('Maria', formal=True)
   - esperado: 'Prezado(a) Maria'
2. Critério: Quando 'formal' for True, a função deve retornar 'Prezado(a) <nome>'.
   - entrada: saudacao('Joao', formal=True)
   - esperado: 'Prezado(a) Joao'
3. Critério: Quando 'formal' for False ou não for especificado, a função deve retornar 'Olá, <nome>'.
   - entrada: saudacao('Zeca')
   - esperado: 'Olá, Zeca'
4. Critério: Quando 'formal' for False ou não for especificado, a função deve retornar 'Olá, <nome>'.
   - entrada: saudacao('Ana', formal=False)
   - esperado: 'Olá, Ana'
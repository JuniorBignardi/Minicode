# Test Plan

1. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'curta' se a senha tiver menos de 8 caracteres.
   - entrada: validar_senha('abc')
   - esperado: ['curta']
2. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'curta' se a senha tiver menos de 8 caracteres.
   - entrada: validar_senha('aaaaaa')
   - esperado: ['curta']
3. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_digito' se a senha não contiver pelo menos um dígito.
   - entrada: validar_senha('Abcdefg')
   - esperado: ['sem_digito']
4. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_digito' se a senha não contiver pelo menos um dígito.
   - entrada: validar_senha('abcdef')
   - esperado: ['sem_digito', 'sem_maiuscula']
5. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_maiuscula' se a senha não contiver pelo menos uma letra maiúscula.
   - entrada: validar_senha('abcde')
   - esperado: ['sem_maiuscula', 'sem_digito']
6. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_maiuscula' se a senha não contiver pelo menos uma letra maiúscula.
   - entrada: validar_senha('ABCDEF')
   - esperado: ['sem_minuscula', 'sem_digito']
7. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_minuscula' se a senha não contiver pelo menos uma letra minúscula.
   - entrada: validar_senha('ABCDEFG')
   - esperado: ['sem_minuscula']
8. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'sem_minuscula' se a senha não contiver pelo menos uma letra minúscula.
   - entrada: validar_senha('AbCdEfG')
   - esperado: []
9. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'com_espaco' se a senha contiver um ou mais espaços.
   - entrada: validar_senha('   ')
   - esperado: ['com_espaco']
10. Critério: A função `validar_senha(senha)` deve retornar uma lista contendo 'com_espaco' se a senha contiver um ou mais espaços.
   - entrada: validar_senha('abc def')
   - esperado: ['com_espaco']
11. Critério: A função `validar_senha(senha)` deve retornar uma lista vazia se a senha cumprir todos os critérios.
   - entrada: validar_senha('Abcd123!')
   - esperado: []
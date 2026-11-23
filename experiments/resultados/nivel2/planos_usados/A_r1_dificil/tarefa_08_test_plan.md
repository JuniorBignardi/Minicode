# Test Plan

1. Critério: A função validar_senha deve retornar uma lista contendo 'curta' se a senha tiver menos de 8 caracteres.
   - entrada: validar_senha('abc')
   - esperado: ['curta']
2. Critério: A função validar_senha deve retornar uma lista contendo 'sem_digito' se a senha não contiver pelo menos um dígito.
   - entrada: validar_senha('abcdefg')
   - esperado: ['sem_digito']
3. Critério: A função validar_senha deve retornar uma lista contendo 'sem_maiuscula' se a senha não contiver pelo menos uma letra maiúscula.
   - entrada: validar_senha('abcdefg1')
   - esperado: ['sem_maiuscula']
4. Critério: A função validar_senha deve retornar uma lista contendo 'sem_minuscula' se a senha não contiver pelo menos uma letra minúscula.
   - entrada: validar_senha('ABCDEFG1')
   - esperado: ['sem_minuscula']
5. Critério: A função validar_senha deve retornar uma lista contendo 'com_espaco' se a senha contiver pelo menos um espaço.
   - entrada: validar_senha('abc1 Abc')
   - esperado: ['com_espaco']
6. Critério: A função validar_senha deve retornar uma lista vazia se a senha for válida, ou seja, não violar nenhuma das regras mencionadas.
   - entrada: validar_senha('Abc1Abc1')
   - esperado: []
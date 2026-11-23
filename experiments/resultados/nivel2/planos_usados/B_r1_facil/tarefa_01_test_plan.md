# Test Plan

1. Critério: A função deve retornar o fatorial correto para qualquer número inteiro não-negativo.
   - entrada: fatorial(0)
   - esperado: 1
2. Critério: A função deve retornar o fatorial correto para qualquer número inteiro não-negativo.
   - entrada: fatorial(5)
   - esperado: 120
3. Critério: A função deve retornar o fatorial correto para qualquer número inteiro não-negativo.
   - entrada: fatorial(10)
   - esperado: 3628800
4. Critério: A função deve levantar ValueError com a mensagem "n deve ser não-negativo" para qualquer número inteiro negativo.
   - entrada: fatorial(-1)
   - esperado: ValueError: n deve ser não-negativo
5. Critério: A função deve levantar ValueError com a mensagem "n deve ser não-negativo" para qualquer número inteiro negativo.
   - entrada: fatorial(-5)
   - esperado: ValueError: n deve ser não-negativo
6. Critério: A função deve levantar ValueError com a mensagem "n deve ser não-negativo" para qualquer número inteiro negativo.
   - entrada: fatorial(3.5)
   - esperado: ValueError: n deve ser um número inteiro
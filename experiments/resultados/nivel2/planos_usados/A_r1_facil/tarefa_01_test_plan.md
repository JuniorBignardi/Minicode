# Test Plan

1. Critério: A função fatorial(n) deve retornar o fatorial de n para valores não negativos de n.
   - entrada: fatorial(0)
   - esperado: 0! = 1
2. Critério: A função fatorial(n) deve retornar o fatorial de n para valores não negativos de n.
   - entrada: fatorial(5)
   - esperado: 5! = 120
3. Critério: A função deve levantar ValueError com a mensagem "n deve ser não negativo" para valores de n negativos.
   - entrada: fatorial(-1)
   - esperado: ValueError: n deve ser não negativo
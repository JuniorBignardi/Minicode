# Test Plan

1. Critério: A função `fibonacci(n)` retorna 0 quando chamada com `fibonacci(0)`.
   - entrada: fibonacci(0)
   - esperado: 0
2. Critério: A função `fibonacci(n)` retorna 1 quando chamada com `fibonacci(1)`.
   - entrada: fibonacci(1)
   - esperado: 1
3. Critério: A função `fibonacci(n)` levanta um `ValueError` quando chamada com um valor negativo para `n`.
   - entrada: fibonacci(-1)
   - esperado: ValueError
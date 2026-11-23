# Test Plan

1. Critério: A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores de `n` não negativos.
   - entrada: fibonacci(0)
   - esperado: 0
2. Critério: A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores de `n` não negativos.
   - entrada: fibonacci(1)
   - esperado: 1
3. Critério: A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores de `n` não negativos.
   - entrada: fibonacci(6)
   - esperado: 8
4. Critério: A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores de `n` não negativos.
   - entrada: fibonacci(10)
   - esperado: 55
5. Critério: A função `fibonacci(n)` deve levantar uma exceção `ValueError` quando `n` é negativo.
   - entrada: fibonacci(-1)
   - esperado: ValueError
6. Critério: A função `fibonacci(n)` deve levantar uma exceção `ValueError` quando `n` é negativo.
   - entrada: fibonacci(-5)
   - esperado: ValueError
# Test Plan

1. Critério: A função `maior` deve retornar o maior número da lista, independentemente dos números serem positivos ou negativos.
   - entrada: maior([5, -2, 8, 1])
   - esperado: 8
2. Critério: A função `maior` deve retornar o maior número da lista, independentemente dos números serem positivos ou negativos.
   - entrada: maior([-7, -3, -10, -2])
   - esperado: -2
3. Critério: A função deve retornar `None` ou lançar uma exceção se a lista estiver vazia.
   - entrada: maior([])
   - esperado: None
4. Critério: A função `maior` deve retornar o maior número da lista, independentemente dos números serem positivos ou negativos.
   - entrada: maior([0, -1, 0, 10])
   - esperado: 10
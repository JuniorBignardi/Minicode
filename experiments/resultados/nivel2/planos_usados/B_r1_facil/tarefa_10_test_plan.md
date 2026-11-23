# Test Plan

1. Critério: Os testes devem verificar que a função `adicionar` adiciona corretamente a quantidade de um item ao estoque.
   - entrada: adicionar('caneta', 5); estoque['caneta']
   - esperado: 5
2. Critério: Os testes devem verificar que a função `adicionar` adiciona corretamente a quantidade de um item ao estoque.
   - entrada: adicionar('caneta', 10); estoque['caneta']
   - esperado: 15
3. Critério: Os testes devem verificar que a função `adicionar` cria uma nova entrada no estoque se o item não existir.
   - entrada: adicionar('lapiseira', 7); estoque['lapiseira']
   - esperado: 7
4. Critério: Os testes devem verificar que a função `adicionar` cria uma nova entrada no estoque se o item não existir.
   - entrada: adicionar('caderno', 3); estoque['caderno']
   - esperado: 3
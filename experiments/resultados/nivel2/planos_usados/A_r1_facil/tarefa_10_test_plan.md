# Test Plan

1. Critério: Os testes devem verificar que a função `adicionar` adiciona a quantidade correta de um item ao estoque.
   - entrada: adicionar('maçã', 10) em um estoque inicialmente vazio
   - esperado: O estoque deve conter {'maçã': 10}
2. Critério: Os testes devem verificar que a função `adicionar` atualiza corretamente o estoque quando o item já existe.
   - entrada: adicionar('maçã', 5) em um estoque que já contém {'maçã': 10}
   - esperado: O estoque deve conter {'maçã': 15}
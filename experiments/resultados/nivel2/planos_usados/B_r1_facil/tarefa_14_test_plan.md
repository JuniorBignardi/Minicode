# Test Plan

1. Critério: A função `area_quadrado` deve chamar a função `area_retangulo` para calcular a área de um quadrado.
   - entrada: area_quadrado(5)
   - esperado: 25
2. Critério: A função `area_quadrado` deve chamar a função `area_retangulo` para calcular a área de um quadrado.
   - entrada: area_quadrado(3)
   - esperado: 9
3. Critério: A função `area_quadrado` deve passar todos os testes em `tests/test_original.py` após a refatoração.
   - entrada: import tests; tests.run_tests()
   - esperado: Todos os testes devem passar sem erros ou falhas.
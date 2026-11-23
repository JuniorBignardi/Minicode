# Test Plan

1. Critério: A função area_quadrado deve chamar a função area_retangulo com argumentos adequados.
   - entrada: area_quadrado(4)
   - esperado: area_retangulo(4, 4) = 16
2. Critério: Os testes em tests/test_original.py devem continuar passando após a refatoração.
   - entrada: Executar todos os testes em tests/test_original.py
   - esperado: Todos os testes passam
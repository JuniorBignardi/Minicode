# Test Plan

1. Critério: A função `arredondar_moeda(valor)` deve ser criada no arquivo `precos.py`.
   - entrada: Chamar a função `arredondar_moeda(1.2345)`
   - esperado: 1.23
2. Critério: Todas as chamadas de `round(..., 2)` devem ser substituídas pela função `arredondar_moeda(valor)`.
   - entrada: Chamar a função `calcular_total([{'quantidade': 2, 'preco': 1.2345}])`
   - esperado: 2.46
3. Critério: Todos os testes em `tests/test_original.py` devem continuar passando após a refatoração.
   - entrada: Executar todos os testes em `tests/test_original.py`
   - esperado: Todos os testes passam sem falhas
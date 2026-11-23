# Test Plan

1. Critério: A função `media` deve calcular a média correta de uma lista de números.
   - entrada: media([10, 20, 30])
   - esperado: 20.0
2. Critério: A função `media` deve calcular a média correta de uma lista de números.
   - entrada: media([-5, -2, 0, 2, 7])
   - esperado: 1.0
3. Critério: A função `media` deve calcular a média correta de uma lista de números.
   - entrada: media([])
   - esperado: 0.0
4. Critério: Os testes em `tests/test_original.py` devem passar sem erros.
   - entrada: import calc; calc.media([1, 2, 3])
   - esperado: 2.0
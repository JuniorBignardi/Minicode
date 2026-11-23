# Test Plan

1. Critério: A função `media` em `calc.py` deve retornar o valor médio correto da lista de números.
   - entrada: media([1, 2, 3, 4, 5])
   - esperado: (1 + 2 + 3 + 4 + 5) / 5 = 3
2. Critério: O teste `test_media` em `tests/test_original.py` deve passar sem falhas.
   - entrada: test_media([1, 2, 3, 4, 5])
   - esperado: O teste deve verificar se a função `media([1, 2, 3, 4, 5])` retorna 3.
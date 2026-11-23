# Test Plan

1. Critério: A função deve unir intervalos que se tocam (por exemplo, `(1, 3)` e `(3, 5)` devem ser combinados em `(1, 5)`).
   - entrada: mesclar([(1, 3), (3, 5)])
   - esperado: [(1, 5)]
2. Critério: A função deve funcionar corretamente com uma lista de intervalos que não está ordenada.
   - entrada: mesclar([(3, 5), (1, 3), (6, 8)])
   - esperado: [(1, 5), (6, 8)]
3. Critério: A função deve manter a funcionalidade existente de unir intervalos que se sobrepõem.
   - entrada: mesclar([(1, 3), (2, 4), (5, 7)])
   - esperado: [(1, 4), (5, 7)]
4. Critério: A função deve unir intervalos que se tocam (por exemplo, `(1, 3)` e `(3, 5)` devem ser combinados em `(1, 5)`).
   - entrada: mesclar([(5, 7), (7, 9)])
   - esperado: [(5, 9)]
5. Critério: A função deve funcionar corretamente com uma lista de intervalos que não está ordenada.
   - entrada: mesclar([(10, 12), (5, 7), (7, 9)])
   - esperado: [(5, 9), (10, 12)]
6. Critério: A função deve manter a funcionalidade existente de unir intervalos que se sobrepõem.
   - entrada: mesclar([(1, 3), (2, 4), (3, 5)])
   - esperado: [(1, 5)]
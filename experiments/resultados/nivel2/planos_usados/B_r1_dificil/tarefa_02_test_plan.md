# Test Plan

1. Critério: A função deve retornar uma lista de intervalos mesclados corretamente, mesmo quando os intervalos se tocam (por exemplo, (1, 3) e (3, 5) devem ser mesclados em (1, 5)).
   - entrada: mesclar([(1, 3), (3, 5)])
   - esperado: [(1, 5)]
2. Critério: A função deve funcionar corretamente quando a lista de intervalos não está ordenada, mesclando os intervalos conforme necessário e retornando a lista de intervalos mesclados em ordem crescente.
   - entrada: mesclar([(5, 7), (1, 3), (9, 11)])
   - esperado: [(1, 7), (9, 11)]
3. Critério: A função deve retornar uma lista de intervalos mesclados corretamente, mesmo quando os intervalos se tocam (por exemplo, (1, 3) e (3, 5) devem ser mesclados em (1, 5)).
   - entrada: mesclar([(10, 12), (6, 8)])
   - esperado: [(6, 12)]
4. Critério: A função deve funcionar corretamente quando a lista de intervalos não está ordenada, mesclando os intervalos conforme necessário e retornando a lista de intervalos mesclados em ordem crescente.
   - entrada: mesclar([(-5, -3), (-1, 0), (2, 4)])
   - esperado: [(-5, -3), (-1, 4)]
5. Critério: A função deve funcionar corretamente quando a lista de intervalos não está ordenada, mesclando os intervalos conforme necessário e retornando a lista de intervalos mesclados em ordem crescente.
   - entrada: mesclar([(2, 4), (1, 3), (5, 7)])
   - esperado: [(1, 4), (5, 7)]
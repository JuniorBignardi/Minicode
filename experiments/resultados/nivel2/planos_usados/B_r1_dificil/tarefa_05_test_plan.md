# Test Plan

1. Critério: A função `perimetro(pontos)` deve retornar o perímetro do polígono formado pelos pontos fornecidos, calculando a distância entre cada par de pontos consecutivos usando a função `distancia`.
   - entrada: perimetro([(0, 0), (3, 0), (3, 4), (0, 0)])
   - esperado: 10.0
2. Critério: A função `perimetro(pontos)` deve retornar o perímetro do polígono formado pelos pontos fornecidos, calculando a distância entre cada par de pontos consecutivos usando a função `distancia`.
   - entrada: perimetro([(-1, -1), (0, 0), (1, -1)])
   - esperado: 4.0
3. Critério: Se a lista de pontos contiver menos de 3 pontos, a função deve levantar uma exceção `ValueError`.
   - entrada: perimetro([(1, 2)])
   - esperado: ValueError
4. Critério: Se a lista de pontos contiver menos de 3 pontos, a função deve levantar uma exceção `ValueError`.
   - entrada: perimetro([])
   - esperado: ValueError
5. Critério: A função `perimetro(pontos)` deve retornar o perímetro do polígono formado pelos pontos fornecidos, calculando a distância entre cada par de pontos consecutivos usando a função `distancia`.
   - entrada: perimetro([(-2, -2), (-2, 2), (2, 2), (2, -2)])
   - esperado: 16.0
# Test Plan

1. Critério: A função `perimetro(pontos)` deve levantar `ValueError` se o número de pontos for menor que 3.
   - entrada: perimetro([(0, 0)])
   - esperado: ValueError
2. Critério: A função `perimetro(pontos)` deve retornar o perímetro correto de um polígono formado pelos pontos fornecidos.
   - entrada: perimetro([(0, 0), (1, 0), (1, 1)])
   - esperado: distancia((0, 0), (1, 0)) + distancia((1, 0), (1, 1)) + distancia((1, 1), (0, 0)) = 1 + 1 + sqrt(2) = 2 + sqrt(2)
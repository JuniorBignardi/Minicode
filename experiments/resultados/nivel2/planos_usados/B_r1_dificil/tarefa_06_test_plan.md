# Test Plan

1. Critério: A função `arredondar_moeda(valor)` deve arredondar corretamente para duas casas decimais.
   - entrada: arredondar_moeda(1.6)
   - esperado: 1.60
2. Critério: A função `arredondar_moeda(valor)` deve arredondar corretamente para duas casas decimais.
   - entrada: arredondar_moeda(2.5)
   - esperado: 2.50
3. Critério: A função `arredondar_moeda(valor)` deve arredondar corretamente para duas casas decimais.
   - entrada: arredondar_moeda(3.14159)
   - esperado: 3.14
4. Critério: As funções `preco_com_imposto`, `preco_com_desconto`, e `preco_final` devem funcionar exatamente como antes, com os mesmos resultados de teste.
   - entrada: preco_com_imposto(preco_com_desconto(preco_final(100)))
   - esperado: preco_com_imposto(preco_com_desconto(arredondar_moeda(100))) = 100.0
5. Critério: As funções `preco_com_imposto`, `preco_com_desconto`, e `preco_final` devem funcionar exatamente como antes, com os mesmos resultados de teste.
   - entrada: preco_com_imposto(preco_com_desconto(preco_final(80)))
   - esperado: preco_com_imposto(preco_com_desconto(arredondar_moeda(80))) = 80.0
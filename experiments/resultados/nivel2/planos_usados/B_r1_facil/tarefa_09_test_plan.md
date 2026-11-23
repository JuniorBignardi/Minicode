# Test Plan

1. Critério: A função 'preco_final' deve aceitar um parâmetro opcional 'desconto' com valor padrão 0.
   - entrada: preco_final(100, desconto=None)
   - esperado: 100
2. Critério: Quando 'desconto' é 0, o preço final deve ser igual ao preço original.
   - entrada: preco_final(50, desconto=0)
   - esperado: 50.0
3. Critério: Quando 'desconto' é um valor diferente de 0, o preço final deve ser calculado subtraindo o valor do desconto do preço original.
   - entrada: preco_final(80, desconto=20)
   - esperado: 64
4. Critério: Quando 'desconto' é um valor diferente de 0, o preço final deve ser calculado subtraindo o valor do desconto do preço original.
   - entrada: preco_final(75, desconto=15)
   - esperado: 63.75
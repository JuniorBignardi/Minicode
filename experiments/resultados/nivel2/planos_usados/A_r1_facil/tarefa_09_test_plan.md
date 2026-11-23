# Test Plan

1. Critério: A função 'preco_final' deve aceitar o parâmetro opcional 'desconto'.
   - entrada: preco_final(preco=100)
   - esperado: 100
2. Critério: Quando o parâmetro 'desconto' for omitido ou igual a 0, o preço final deve ser igual ao preço original.
   - entrada: preco_final(preco=100)
   - esperado: 100
3. Critério: Quando o parâmetro 'desconto' for um valor maior que 0, o preço final deve ser calculado subtraindo o percentual do desconto do preço original.
   - entrada: preco_final(preco=100, desconto=10)
   - esperado: 100 - (100 * 10 / 100) = 90
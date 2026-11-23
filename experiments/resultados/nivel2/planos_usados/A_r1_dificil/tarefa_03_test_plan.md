# Test Plan

1. Critério: O método adicionar deve adicionar a quantidade de um item ao carrinho se o item já existir.
   - entrada: carrinho.adicionar('maçã', 1.5, 3)
carrinho.adicionar('maçã', 1.5, 2)
   - esperado: A quantidade total de maçã deve ser 5.
2. Critério: O método remover deve levantar KeyError se o item não estiver presente no carrinho.
   - entrada: carrinho.remover('banana')
   - esperado: KeyError: 'Item não está no carrinho'
3. Critério: O método total deve retornar a soma correta do preço multiplicado pela quantidade de cada item.
   - entrada: carrinho.adicionar('maçã', 1.5, 3)
carrinho.adicionar('banana', 2.0, 2)
carrinho.total()
   - esperado: 1.5 * 3 + 2.0 * 2 = 8.5
4. Critério: O método adicionar deve adicionar a quantidade de um item ao carrinho se o item já existir.
   - entrada: carrinho.adicionar('laranja', 0.5, 10)
carrinho.adicionar('laranja', 0.5, -5)
   - esperado: ValueError: 'Quantidade deve ser maior que zero'
5. Critério: O método adicionar deve adicionar a quantidade de um item ao carrinho se o item já existir.
   - entrada: carrinho.adicionar('uva', -1.0, 5)
   - esperado: ValueError: 'Preço deve ser maior ou igual a zero'
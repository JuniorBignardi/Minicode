# Test Plan

1. Critério: Deve ser possível adicionar um item ao carrinho com a função adicionar(item, preco, qtd=1), que levanta ValueError se qtd <= 0 ou preco < 0.
   - entrada: carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); len(carrinho.itens)
   - esperado: 1
2. Critério: Deve ser possível adicionar um item ao carrinho com a função adicionar(item, preco, qtd=1), que levanta ValueError se qtd <= 0 ou preco < 0.
   - entrada: carrinho = Carrinho(); try: carrinho.adicionar('caneta', 2.5, -1); except ValueError: True
   - esperado: ValueError
3. Critério: Deve ser possível adicionar um item ao carrinho com a função adicionar(item, preco, qtd=1), que levanta ValueError se qtd <= 0 ou preco < 0.
   - entrada: carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3)
   - esperado: None
4. Critério: Deve ser possível remover um item do carrinho com a função remover(item), que levanta KeyError se o item não está no carrinho.
   - entrada: carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.remover('caneta'); len(carrinho.itens)
   - esperado: 0
5. Critério: A função total() deve retornar a soma de preco * qtd para todos os itens no carrinho.
   - entrada: carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.adicionar('lapiseira', 5.0, 2); carrinho.total()
   - esperado: 17.0
6. Critério: Adicionar o mesmo item de novo deve somar a quantidade.
   - entrada: carrinho = Carrinho(); carrinho.adicionar('chave', 10.0, 2); carrinho.adicionar('chave', 10.0, 4); carrinho.total()
   - esperado: 50.0
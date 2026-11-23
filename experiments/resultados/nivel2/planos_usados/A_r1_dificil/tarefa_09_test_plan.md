# Test Plan

1. Critério: Os testes em tests/test_original.py devem passar após a correção.
   - entrada: Executar todos os testes em tests/test_original.py
   - esperado: Todos os testes devem passar
2. Critério: Os métodos desempilhar e topo devem verificar se a pilha está vazia antes de realizar a operação, levantando IndexError se for o caso.
   - entrada: pilha = Pilha()
pilha.desempilhar()
   - esperado: IndexError
3. Critério: Os métodos desempilhar e topo devem verificar se a pilha está vazia antes de realizar a operação, levantando IndexError se for o caso.
   - entrada: pilha = Pilha()
pilha.topo()
   - esperado: IndexError
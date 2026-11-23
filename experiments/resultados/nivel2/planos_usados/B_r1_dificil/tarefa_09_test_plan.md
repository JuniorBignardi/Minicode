# Test Plan

1. Critério: Os testes em pilha.py devem passar sem falhas após a correção.
   - entrada: pilha = Pilha(); pilha.empilhar(10); pilha.desempilhar()
   - esperado: 10
2. Critério: Ao tentar desempilhar ou obter o topo de uma pilha vazia, deve ser levantado um IndexError.
   - entrada: pilha = Pilha(); pilha.desempilhar()
   - esperado: IndexError
3. Critério: Ao tentar desempilhar ou obter o topo de uma pilha vazia, deve ser levantado um IndexError.
   - entrada: pilha = Pilha(); pilha.topo()
   - esperado: IndexError
4. Critério: A função test_lifo em test_original.py deve passar sem falhas.
   - entrada: from pilha import Pilha; Pilha().test_lifo()
   - esperado: None
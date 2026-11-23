# Test Plan

1. Critério: Ao chamar `criar_usuario('Ana', 30)`, a função deve retornar o dicionário `{'nome': 'Ana', 'idade': 30}`.
   - entrada: criar_usuario('Ana', 30)
   - esperado: {'nome': 'Ana', 'idade': 30}
2. Critério: Ao chamar `criar_usuario('', 30)`, a função deve levantar uma exceção `ValueError` com a mensagem "Nome não pode ser vazio".
   - entrada: criar_usuario('', 30)
   - esperado: ValueError: Nome não pode ser vazio
3. Critério: Ao chamar `criar_usuario('Ana', -5)`, a função deve levantar uma exceção `ValueError` com a mensagem "Idade deve estar entre 0 e 150".
   - entrada: criar_usuario('Ana', -5)
   - esperado: ValueError: Idade deve estar entre 0 e 150
4. Critério: Ao chamar `criar_usuario('Ana', 151)`, a função deve levantar uma exceção `ValueError` com a mensagem "Idade deve estar entre 0 e 150".
   - entrada: criar_usuario('Ana', 151)
   - esperado: ValueError: Idade deve estar entre 0 e 150
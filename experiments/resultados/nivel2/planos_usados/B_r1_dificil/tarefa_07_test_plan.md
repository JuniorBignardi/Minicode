# Test Plan

1. Critério: A função `listar` deve aceitar dois parâmetros opcionais: `apenas_pendentes` (padrão `False`) e `prioridade` (padrão `None`).
   - entrada: listar(['Tarefa 1'])
   - esperado: [{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': None}]
2. Critério: Se `apenas_pendentes` for `True`, a função deve retornar apenas tarefas com 'feita' igual a `False`.
   - entrada: listar([{'titulo': 'Tarefa A', 'feita': True}, {'titulo': 'Tarefa B', 'feita': False}], apenas_pendentes=True)
   - esperado: [{'titulo': 'Tarefa B', 'feita': False}]
3. Critério: Se `prioridade` for especificado, a função deve retornar apenas tarefas com a prioridade especificada.
   - entrada: listar([{'titulo': 'Prioritária 1', 'prioridade': 5}], prioridade=5)
   - esperado: [{'titulo': 'Prioritária 1', 'feita': False, 'prioridade': 5}]
4. Critério: Se ambos os parâmetros forem omitidos, a função deve retornar todas as tarefas como faz atualmente.
   - entrada: listar([{'titulo': 'Sem Prioridade'}, {'titulo': 'Com Prioridade'}])
   - esperado: [{'titulo': 'Sem Prioridade', 'feita': False, 'prioridade': None}, {'titulo': 'Com Prioridade', 'feita': False, 'prioridade': None}]
5. Critério: Se `prioridade` for especificado, a função deve retornar apenas tarefas com a prioridade especificada.
   - entrada: listar([{'titulo': 'Tarefa X', 'prioridade': 3}], prioridade=7)
   - esperado: []
6. Critério: A função `listar` deve aceitar dois parâmetros opcionais: `apenas_pendentes` (padrão `False`) e `prioridade` (padrão `None`).
   - entrada: listar([], apenas_pendentes=True, prioridade=2)
   - esperado: []
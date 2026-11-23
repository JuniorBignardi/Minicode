# Test Plan

1. Critério: A função `listar(tarefas, apenas_pendentes=False, prioridade=None)` deve retornar todas as tarefas quando os parâmetros adicionais não são especificados.
   - entrada: listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}])
   - esperado: [{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}]
2. Critério: A função deve omitir as tarefas com a chave 'feita' igual a True quando apenas_pendentes=True.
   - entrada: listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}], apenas_pendentes=True)
   - esperado: [{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}]
3. Critério: A função deve retornar apenas tarefas com a chave 'prioridade' igual ao valor especificado quando prioridade é um valor diferente de None.
   - entrada: listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}], prioridade='media')
   - esperado: [{'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}]
4. Critério: A função deve retornar todas as tarefas quando prioridade=None.
   - entrada: listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}], prioridade=None)
   - esperado: [{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'prioridade': 'baixa'}, {'titulo': 'Tarefa 3', 'feita': False, 'prioridade': 'media'}]
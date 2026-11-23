# Test Plan

1. Critério: A função ler_csv deve retornar uma lista de dicionários com a estrutura correta baseada no conteúdo CSV fornecido.
   - entrada: texto = 'nome,idade\nAlice,30\nBob,25'
   - esperado: resultado = [{'nome': 'Alice', 'idade': '30'}, {'nome': 'Bob', 'idade': '25'}]
2. Critério: A função deve levantar ValueError se a quantidade de campos em alguma linha for diferente da quantidade de campos no cabeçalho.
   - entrada: texto = 'nome,idade\nAlice,30\nBob,25,extra'
   - esperado: ValueError
3. Critério: A função deve levantar ValueError se a quantidade de campos em alguma linha for diferente da quantidade de campos no cabeçalho.
   - entrada: texto = 'nome,idade\nAlice,30\nBob,25\nCharlie'
   - esperado: ValueError
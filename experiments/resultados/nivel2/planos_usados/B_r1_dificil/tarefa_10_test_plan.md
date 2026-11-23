# Test Plan

1. Critério: A função ler_csv(texto) deve retornar uma lista de dicionários onde os chaves são os nomes dos campos extraídos da primeira linha do CSV.
   - entrada: ler_csv('nome,idade\nAna,23\nBruno,30')
   - esperado: [{'nome': 'Ana', 'idade': '23'}, {'nome': 'Bruno', 'idade': '30'}]
2. Critério: Caso a função detecte que uma linha tem um número diferente de campos do que o cabeçalho, deve levantar um ValueError.
   - entrada: ler_csv('nome,idade\nAna\nBruno,30')
   - esperado: ValueError
3. Critério: Caso a função detecte que uma linha tem um número diferente de campos do que o cabeçalho, deve levantar um ValueError.
   - entrada: ler_csv('nome,idade\nAna,23,45')
   - esperado: ValueError
4. Critério: Caso a função detecte que uma linha tem um número diferente de campos do que o cabeçalho, deve levantar um ValueError.
   - entrada: ler_csv('a,b\na\nc')
   - esperado: ValueError
5. Critério: Caso a função detecte que uma linha tem um número diferente de campos do que o cabeçalho, deve levantar um ValueError.
   - entrada: ler_csv('x,y\nx,1\nz')
   - esperado: ValueError
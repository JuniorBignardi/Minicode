# Test Plan

1. Critério: A função contar_linhas deve retornar um número inteiro representando o número de linhas não vazias em um arquivo.
   - entrada: contar_linhas('dados.txt')
   - esperado: 5
2. Critério: A função palavras_unicas deve retornar uma string com palavras únicas em minúsculas, separadas por espaços ou quebras de linha.
   - entrada: palavras_unicas('dados.txt')
   - esperado: 'olá mundo teste python'
3. Critério: Ambas as funções devem levantar uma exceção FileNotFoundError se o arquivo não existir.
   - entrada: contar_linhas('inexistente.txt')
   - esperado: FileNotFoundError
4. Critério: Ambas as funções devem levantar uma exceção FileNotFoundError se o arquivo não existir.
   - entrada: palavras_unicas('inexistente.txt')
   - esperado: FileNotFoundError
# Test Plan

1. Critério: A função contar_linhas(caminho) deve retornar o número correto de linhas não vazias no arquivo especificado.
   - entrada: contar_linhas(tmp_path / 'arquivo.txt') onde 'arquivo.txt' contém as linhas 'linha1\nlinha2\n\nlinha3'
   - esperado: 3
2. Critério: A função palavras_unicas(caminho) deve retornar uma lista ordenada de palavras únicas em minúsculas do arquivo especificado.
   - entrada: palavras_unicas(tmp_path / 'arquivo.txt') onde 'arquivo.txt' contém as linhas 'A\nB\na\na\nb\nc'
   - esperado: a b c
3. Critério: Ambas as funções devem levantar FileNotFoundError se o arquivo não existir.
   - entrada: contar_linhas(tmp_path / 'arquivo_inexistente.txt')
   - esperado: FileNotFoundError
4. Critério: Ambas as funções devem levantar FileNotFoundError se o arquivo não existir.
   - entrada: palavras_unicas(tmp_path / 'arquivo_inexistente.txt')
   - esperado: FileNotFoundError
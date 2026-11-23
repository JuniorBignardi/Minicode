# Test Plan

1. Critério: A função `criar_usuario` deve levantar `ValueError` se o parâmetro `nome` for uma string vazia.
   - entrada: criar_usuario(nome='', idade=25)
   - esperado: ValueError
2. Critério: A função `criar_usuario` deve levantar `ValueError` se o parâmetro `idade` for menor que 0 ou maior que 150.
   - entrada: criar_usuario(nome='João', idade=-1)
   - esperado: ValueError
3. Critério: A função `criar_usuario` deve levantar `ValueError` se o parâmetro `idade` for menor que 0 ou maior que 150.
   - entrada: criar_usuario(nome='Maria', idade=151)
   - esperado: ValueError
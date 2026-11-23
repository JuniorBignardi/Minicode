# Test Plan

1. Critério: A função `validar_email(email)` deve retornar `True` para um email válido, como 'usuario@dominio.com'.
   - entrada: validar_email('usuario@dominio.com')
   - esperado: True
2. Critério: A função `validar_email(email)` deve retornar `False` para um email inválido, como '@dominio.com' ou 'usuario.domino'.
   - entrada: validar_email('@dominio.com')
   - esperado: False
3. Critério: A função `validar_email(email)` deve retornar `False` para um email inválido, como '@dominio.com' ou 'usuario.domino'.
   - entrada: validar_email('usuario.domino')
   - esperado: False
4. Critério: A função `validar_email(email)` deve retornar `False` para um email inválido, como '@dominio.com' ou 'usuario.domino'.
   - entrada: validar_email('usuario@')
   - esperado: False
5. Critério: A função `validar_email(email)` deve retornar `False` para um email inválido, como '@dominio.com' ou 'usuario.domino'.
   - entrada: validar_email('usuario@dominio')
   - esperado: False
# Respostas do Colab, lidas e pontuadas


## real_ajustado

### 0: dificil_1 | formato ok | plano válido | notas: 3 corretos, 1 errados, 0 inavaliáveis
- [correto] `r=RepositorioUsuarios(); r.adicionar('ana', 'senha'); r.remover('ana')` → `None`
- [errado] `r=RepositorioUsuarios(); s=ServicoUsuarios(r); s.excluir_usuario('ana')` → `None`
- [correto] `r=RepositorioUsuarios(); s=ServicoUsuarios(r); s.excluir_usuario('inexistente')` → `KeyError`
- [correto] `s=ServicoUsuarios(RepositorioUsuarios()); s.excluir_usuario('admin')` → `KeyError`
### 1: dificil_2 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `mesclar([(1, 3), (3, 5)])` → `[(1, 5)]`
- [correto] `mesclar([(10, 12), (8, 10), (9, 11)])` → `[(8, 12)]`
- [correto] `mesclar([(1, 3), (5, 7)])` → `[(1, 3), (5, 7)]`
- [correto] `mesclar([(2, 6), (1, 3), (4, 8)])` → `[(1, 8)]`
### 2: dificil_3 | formato ok | plano válido | notas: 4 corretos, 3 errados, 0 inavaliáveis
- [correto] `c = Carrinho(); c.adicionar('caneta', 2.5, 2); c.total()` → `5.0`
- [correto] `c = Carrinho(); c.adicionar('caneta', 2.5, -1)` → `ValueError`
- [errado] `c = Carrinho(); c.adicionar('caneta', 2.5, 2); c.adicionar('caneta', 2.5, 3)` → `6.0`
- [correto] `c = Carrinho(); c.adicionar('caneta', 2.5, 2); c.remover('caneta'); c.total()` → `0.0`
- [correto] `c = Carrinho(); c.remover('inexistente')` → `KeyError`
- [errado] `c = Carrinho(); c.adicionar('caneta', 2.5, 2); c.adicionar('lapiseira', 5.0, 1); c.total()` → `12.5`
- [errado] `c = Carrinho(); c.adicionar('item', 10.0, 3); c.adicionar('item', 10.0, 4); c.total()` → `50.0`
### 3: dificil_4 | formato ok | plano válido | notas: 0 corretos, 0 errados, 4 inavaliáveis
- [inavaliavel] `contar_linhas('dados.txt')` → `4`
- [inavaliavel] `palavras_unicas('dados.txt')` → `'olá mundo python'`
- [inavaliavel] `contar_linhas('inexistente.txt')` → `FileNotFoundError`
- [inavaliavel] `palavras_unicas('inexistente.txt')` → `FileNotFoundError`
### 4: dificil_5 | formato ok | plano válido | notas: 4 corretos, 1 errados, 0 inavaliáveis
- [correto] `perimetro([(0, 0), (3, 0), (3, 4), (0, 0)])` → `12.0`
- [correto] `perimetro([(-1, -1), (-1, 1), (1, 1), (1, -1)])` → `8.0`
- [correto] `perimetro([(1, 1)])` → `ValueError`
- [correto] `perimetro([])` → `ValueError`
- [errado] `perimetro((0, 0), (1, 0), (1, 1))` → `3.0`
### 5: dificil_6 | formato ok | plano válido | notas: 0 corretos, 4 errados, 0 inavaliáveis
- [errado] `preco_com_imposto(10)` → `10.5`
- [errado] `preco_com_desconto(8)` → `7.6`
- [errado] `preco_final(9, 0.1)` → `8.1`
- [errado] `import tests; tests.run()` → `None`
### 6: dificil_7 | formato ok | plano válido | notas: 1 corretos, 3 errados, 0 inavaliáveis
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2})` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}, apenas_pendentes=True)` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}, prioridade=2)` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [correto] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}, {'titulo': 'Tarefa 2', 'feita': True, 'priori` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}, {'titulo': '`
### 7: dificil_8 | formato ok | plano válido | notas: 1 corretos, 3 errados, 0 inavaliáveis
- [errado] `validar_senha('abc')` → `['curta']`
- [errado] `validar_senha('a b')` → `['sem_digito', 'sem_maiuscula', 'sem_minuscula', 'com_espaco']`
- [errado] `validar_senha('abcde')` → `['sem_digito', 'sem_maiuscula']`
- [correto] `validar_senha('Abc12345')` → `[]`
### 8: dificil_9 | formato ok | plano válido | notas: 3 corretos, 0 errados, 1 inavaliáveis
- [correto] `pilha = Pilha(); pilha.desempilhar()` → `IndexError`
- [correto] `pilha = Pilha(); pilha.topo()` → `IndexError`
- [correto] `pilha = Pilha(); pilha.desempilhar() or pilha.topo()` → `IndexError`
- [inavaliavel] `import unittest; suite = unittest.TestLoader().loadTestsFromTestCase(tests.test_pilha); unittest.TextTestRunne` → `None`
### 9: dificil_10 | formato ok | plano válido | notas: 3 corretos, 1 errados, 0 inavaliáveis
- [correto] `ler_csv('nome,idade\nAna,23')` → `[{'nome': 'Ana', 'idade': '23'}]`
- [errado] `ler_csv('a,b\nc,d\ne,f')` → `[{'b': 'd'}, {'f': 'e'}]`
- [correto] `ler_csv('x,y\nz')` → `ValueError`
- [correto] `ler_csv('id,nome,soma\n1,A,10\n2,B,20')` → `[{'soma': '10', 'nome': 'A', 'id': '1'}, {'soma': '20', 'nome': 'B', '`
### 10: dificil_1 | formato ok | plano válido | notas: 3 corretos, 1 errados, 0 inavaliáveis
- [correto] `r=RepositorioUsuarios(); r.adicionar('ana', 'senha'); r.remover('ana')` → `None`
- [correto] `r=RepositorioUsuarios(); r.remover('inexistente')` → `KeyError`
- [errado] `s=ServicoUsuarios(); s.excluir_usuario('ana')` → `None`
- [correto] `s=ServicoUsuarios(); s.excluir_usuario('inexistente')` → `KeyError`
### 11: dificil_2 | formato ok | plano válido | notas: 0 corretos, 5 errados, 0 inavaliáveis
- [errado] `mesclar([(1, 3), (3, 5)])` → `[1, 5]`
- [errado] `mesclar([(10, 12), (12, 14)])` → `[10, 14]`
- [errado] `mesclar([(5, 7), (2, 4), (9, 11)])` → `[2, 11]`
- [errado] `mesclar([(-5, -3), (-3, -1), (-1, 0)])` → `[-5, 0]`
- [errado] `mesclar([(100, 102), (101, 103), (102, 104)])` → `[100, 104]`
### 12: dificil_3 | formato ok | plano válido | notas: 4 corretos, 5 errados, 0 inavaliáveis
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); len(carrinho.items)` → `1`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('lapiseira', 10, -1)` → `ValueError`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('caderno', 15, 2); carrinho.total()` → `30.0`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('mouse', 50, 0)` → `ValueError`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.remover('caneta'); len(carrinho.items)` → `0`
- [correto] `carrinho = Carrinho(); carrinho.remover('caneta')` → `KeyError`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.adicionar('lapiseira', 5.0, 2); carrinho` → `16.0`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('item1', 10.0, 5); carrinho.adicionar('item2', 20.0, 3); carrinho.to` → `70.0`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('item', 10.0, 4); carrinho.adicionar('item', 10.0, 4); carrinho.tota` → `40.0`
### 13: dificil_4 | formato ok | plano válido | notas: 0 corretos, 0 errados, 4 inavaliáveis
- [inavaliavel] `contar_linhas('exemplo.txt')` → `4`
- [inavaliavel] `palavras_unicas('arquivo_vazio.txt')` → `[]`
- [inavaliavel] `contar_linhas('nao_existe.txt')` → `FileNotFoundError`
- [inavaliavel] `palavras_unicas('nao_existe.txt')` → `FileNotFoundError`
### 14: dificil_5 | formato ok | plano válido | notas: 5 corretos, 0 errados, 0 inavaliáveis
- [correto] `perimetro([(0, 0), (3, 0), (3, 4), (0, 0)])` → `12.0`
- [correto] `perimetro([(-1, -1), (-1, 1), (1, 1), (1, -1)])` → `8.0`
- [correto] `perimetro([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])` → `4.0`
- [correto] `perimetro([(1, 1)])` → `ValueError`
- [correto] `perimetro([])` → `ValueError`
### 15: dificil_6 | formato ok | plano inválido | notas: 2 corretos, 1 errados, 2 inavaliáveis
- [correto] `arredondar_moeda(10)` → `10`
- [correto] `arredondar_moeda(5.678)` → `5.68`
- [inavaliavel] `precos.preco_a[0] = arredondar_moeda(precos.preco_a[0]); preco_a` → `10.0`
- [inavaliavel] `precos.preco_b[0] = arredondar_moeda(precos.preco_b[0]); preco_b` → `9.0`
- [errado] `import tests; tests.run()` → `None`
### 16: dificil_7 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'p` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}]`
- [correto] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': True, 'p` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}]`
- [correto] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': False, '` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titul`
- [correto] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': False, '` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titul`
- [errado] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': False, '` → `[{'titulo': 'Tarefa 2', 'feita': False, 'prioridade': 'baixa'}]`
- [errado] `listar([{'titulo': 'Tarefa 1', 'feita': True, 'prioridade': 'alta'}, {'titulo': 'Tarefa 2', 'feita': False, 'p` → `[]`
### 17: dificil_8 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `validar_senha('Abcdefg')` → `['curta']`
- [correto] `validar_senha('Abcdefg1')` → `[]`
- [errado] `validar_senha('abcdefg')` → `['sem_maiuscula']`
- [errado] `validar_senha('ABCDEF1')` → `['sem_minuscula']`
- [errado] `validar_senha('Abc def')` → `['com_espaco']`
- [correto] `validar_senha('Abcdefgh1')` → `[]`
### 18: dificil_9 | formato ok | plano inválido | notas: 2 corretos, 1 errados, 0 inavaliáveis
- [correto] `pilha = Pilha(); pilha.desempilhar()` → `IndexError`
- [correto] `pilha = Pilha(); pilha.topo()` → `IndexError`
- [errado] `import pilha; pilha.Pilha().desempilhar()` → `None`
### 19: dificil_10 | formato ok | plano válido | notas: 4 corretos, 1 errados, 0 inavaliáveis
- [correto] `ler_csv("nome,idade\nAna,23\n")` → `[{'nome': 'Ana', 'idade': '23'}]`
- [correto] `ler_csv("x,y,z\n10,20,30\n40,50,60")` → `[{'x': '10', 'y': '20', 'z': '30'}, {'x': '40', 'y': '50', 'z': '60'}]`
- [correto] `ler_csv("a,b\n1,2,3")` → `ValueError`
- [errado] `ler_csv("nome,idade\nAna,23")` → `ValueError`
- [correto] `ler_csv("s1,v1,s2\n100,101,102")` → `[{'s1': '100', 'v1': '101', 's2': '102'}]`
### 20: dificil_1 | formato ok | plano válido | notas: 3 corretos, 1 errados, 0 inavaliáveis
- [correto] `r=RepositorioUsuarios(); r.remover(99)` → `KeyError`
- [correto] `r=RepositorioUsuarios(); r.remover('invalid')` → `KeyError`
- [errado] `s=ServicoUsuarios(); s.excluir_usuario(10); r=RepositorioUsuarios(); r.remover(10)` → `None`
- [correto] `s=ServicoUsuarios(); s.excluir_usuario(-1)` → `KeyError`
### 21: dificil_2 | formato ok | plano inválido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `mesclar([(1, 3), (3, 5)])` → `[(1, 5)]`
- [correto] `mesclar([(3, 5), (1, 3)])` → `[(1, 5)]`
- [correto] `mesclar([(1, 2), (2, 3)])` → `[(1, 3)]`
- [correto] `mesclar([(2, 4), (1, 3)])` → `[(1, 4)]`
### 22: dificil_3 | formato ok | plano válido | notas: 5 corretos, 3 errados, 0 inavaliáveis
- [correto] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3)` → `None`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 0, 5)` → `ValueError`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, -1)` → `ValueError`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.total()` → `15.0`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.remover('caneta')` → `None`
- [correto] `carrinho = Carrinho(); carrinho.remover('caneta')` → `KeyError`
- [errado] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.adicionar('lapiseira', 1.5, 2); carrinho` → `12.0`
- [correto] `carrinho = Carrinho(); carrinho.adicionar('caneta', 2.5, 3); carrinho.adicionar('caneta', 2.5, 4); carrinho.to` → `17.5`
### 23: dificil_4 | formato ok | plano válido | notas: 0 corretos, 0 errados, 4 inavaliáveis
- [inavaliavel] `contar_linhas('dados.txt')` → `4`
- [inavaliavel] `palavras_unicas('dados.txt')` → `'ana belo carlo diana'`
- [inavaliavel] `contar_linhas('inexistente.txt')` → `FileNotFoundError`
- [inavaliavel] `palavras_unicas('inexistente.txt')` → `FileNotFoundError`
### 24: dificil_5 | formato ok | plano válido | notas: 5 corretos, 0 errados, 0 inavaliáveis
- [correto] `perimetro([(0, 0), (3, 0), (3, 4), (0, 0)])` → `12.0`
- [correto] `perimetro([(-1, -1), (-1, 1), (1, 1), (1, -1)])` → `8.0`
- [correto] `perimetro([(1, 1)])` → `ValueError`
- [correto] `perimetro([])` → `ValueError`
- [correto] `perimetro((5, 5))` → `ValueError`
### 25: dificil_6 | formato ok | plano inválido | notas: 3 corretos, 4 errados, 0 inavaliáveis
- [correto] `arredondar_moeda(1.6)` → `1.6`
- [correto] `arredondar_moeda(2.5)` → `2.5`
- [correto] `arredondar_moeda(3.14159)` → `3.14`
- [errado] `preco_com_imposto(preco=100, imposto=0.1)` → `90.0`
- [errado] `preco_com_desconto(preco=100, desconto=0.2)` → `80.0`
- [errado] `preco_final(preco=100, preco_com_imposto=90, preco_com_desconto=80)` → `100.0`
- [errado] `import tests; tests.run()` → `None`
### 26: dificil_7 | formato ok | plano válido | notas: 1 corretos, 6 errados, 0 inavaliáveis
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2})` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}, apenas_pendentes=True)` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}, prioridade=2)` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}]`
- [correto] `listar([{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}, {'titulo': 'Tarefa 2', 'feita': True, 'priori` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}, {'titulo': '`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 2}, apenas_pendentes=True, prioridade=2)` → `[]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': True, 'prioridade': 2}, apenas_pendentes=True)` → `[]`
- [errado] `listar({'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}, prioridade=1)` → `[{'titulo': 'Tarefa 1', 'feita': False, 'prioridade': 1}]`
### 27: dificil_8 | formato ok | plano válido | notas: 0 corretos, 5 errados, 0 inavaliáveis
- [errado] `validar_senha('abc')` → `['curta']`
- [errado] `validar_senha('abc')` → `['sem_digito', 'sem_maiuscula', 'sem_minuscula']`
- [errado] `validar_senha('abcdefg')` → `['curta', 'sem_digito', 'sem_maiuscula', 'sem_minuscula']`
- [errado] `validar_senha('abc def')` → `['sem_digito', 'sem_maiuscula', 'sem_minuscula', 'com_posta']`
- [errado] `validar_senha('Abc123')` → `[]`
### 28: dificil_9 | formato ok | plano válido | notas: 2 corretos, 1 errados, 0 inavaliáveis
- [correto] `pilha = Pilha(); pilha.desempilhar()` → `IndexError`
- [correto] `pilha = Pilha(); pilha.topo()` → `IndexError`
- [errado] `import unittest; from pilha import Pilha; unittest.main()` → `None`
### 29: dificil_10 | formato ok | plano válido | notas: 2 corretos, 3 errados, 0 inavaliáveis
- [correto] `ler_csv("nome,idade\nAna,20\nBruno,30")` → `[{'nome': 'Ana', 'idade': '20'}, {'nome': 'Bruno', 'idade': '30'}]`
- [correto] `ler_csv("nome,idade\nAna,20,extra")` → `ValueError`
- [errado] `ler_csv("nome,idade\nAna,20")` → `ValueError`
- [errado] `ler_csv("x,y,z\nx=1,y=2\ny=9,z=8")` → `[{'x': '1', 'y': '2', 'z': '9'}, {'x': 'y', 'y': '9', 'z': '8'}]`
- [errado] `ler_csv("a,b\na,1")` → `ValueError`
### 30: facil_1 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `fatorial(0)` → `1`
- [correto] `fatorial(1)` → `1`
- [correto] `fatorial(5)` → `120`
- [correto] `fatorial(7)` → `5040`
- [correto] `fatorial(-1)` → `ValueError`
- [correto] `fatorial(-5)` → `ValueError`
### 31: facil_2 | formato ok | plano válido | notas: 3 corretos, 2 errados, 0 inavaliáveis
- [errado] `eh_palindromo('A man, a plan, a canal: Panama')` → `True`
- [correto] `eh_palindromo('Ovo')` → `True`
- [correto] `eh_palindromo('Abacaxi')` → `False`
- [correto] `eh_palindromo('Python')` → `False`
- [errado] `eh_palindromo('radar')` → `False`
### 32: facil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
{"casos": [{"criterio": "A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores não negativos de `n`.", "entrada": "fibonacci(0)", "esperado": "0"}, {"criterio": "A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores não negativos de `n`.", "entrada": "fibonacci(1)", "esperado": "1"}, {"criterio": "A função `fibonacci(n)` deve retornar o número correto da sequência de Fibonacci para valores não negativos de `n`.", "en
```
### 33: facil_4 | formato ok | plano válido | notas: 2 corretos, 1 errados, 0 inavaliáveis
- [errado] `contar_palavras('O rato roeu a roupa')` → `{'rato': 1, 'outra': 1, 'roupa': 1}`
- [correto] `contar_palavras('PALAVRA palavra')` → `{'palavra': 2}`
- [correto] `contar_palavras('um dois três um')` → `{'um': 2, 'dois': 1, 'três': 1}`
### 34: facil_5 | formato ok | plano válido | notas: 1 corretos, 1 errados, 0 inavaliáveis
- [correto] `media([10, 20, 30])` → `20.0`
- [errado] `import tests; tests.run_tests()` → `None`
### 35: facil_6 | formato ok | plano inválido | notas: 2 corretos, 3 errados, 0 inavaliáveis
- [correto] `maior([-5, -2, -9])` → `-2`
- [correto] `maior([-7, -3, -10, -1])` → `-1`
- [errado] `maior([0, -100, -200, -50])` → `-50`
- [errado] `maior([])` → `None`
- [errado] `maior([42])` → `None`
### 36: facil_7 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `eh_par(4)` → `True`
- [correto] `eh_par(7)` → `False`
- [correto] `eh_par(0)` → `True`
- [correto] `eh_par(-8)` → `True`
- [correto] `eh_par(-5)` → `False`
- [errado] `import tests.test_original; tests.test_original.run()` → `None`
### 37: facil_8 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `saudacao('Joao')` → `'Olá, Joao'`
- [correto] `saudacao('Maria', formal=True)` → `'Prezado(a) Maria'`
- [correto] `saudacao('Pedro')` → `'Olá, Pedro'`
- [correto] `saudacao('Ana', formal=False)` → `'Olá, Ana'`
### 38: facil_9 | formato ok | plano válido | notas: 3 corretos, 0 errados, 0 inavaliáveis
- [correto] `preco_final(100)` → `100`
- [correto] `preco_final(50, desconto=0)` → `50`
- [correto] `preco_final(80, desconto=10)` → `72.0`
### 39: facil_10 | formato ok | plano válido | notas: 0 corretos, 0 errados, 4 inavaliáveis
- [inavaliavel] `estoque = Estoque(); adicionar(estoque, 'arroz', 5); adicionar(estoque, 'arroz', 3)` → `{'quantidade': 8}`
- [inavaliavel] `estoque = Estoque(); adicionar(estoque, 'feijao', 7); adicionar(estoque, 'feijao', 4)` → `{'quantidade': 11}`
- [inavaliavel] `estoque = Estoque(); adicionar(estoque, 'ovos', 2)` → `{'quantidade': 2}`
- [inavaliavel] `estoque = Estoque(); adicionar(estoque, 'leite', 0)` → `{'quantidade': 0}`
### 40: facil_11 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `eh_primo(2)` → `True`
- [correto] `eh_primo(2)` → `True`
- [correto] `eh_primo(4)` → `False`
- [correto] `eh_primo(4)` → `False`
### 41: facil_12 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `criar_usuario('Ana', 30)` → `{'nome': 'Ana', 'idade': 30}`
- [correto] `criar_usuario('', 30)` → `ValueError`
- [correto] `criar_usuario('Ana', -5)` → `ValueError`
- [correto] `criar_usuario('Ana', 151)` → `ValueError`
### 42: facil_13 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `validar_email('joao@exemplo.com')` → `True`
- [correto] `validar_email('teste@localhost.localdomain')` → `True`
- [correto] `validar_email('@semTexto@teste.com')` → `False`
- [correto] `validar_email('invalido')` → `False`
- [correto] `validar_email('joao@exemplo')` → `False`
- [errado] `validar_email('joao@exemplo.com')` → `False`
### 43: facil_14 | formato ok | plano válido | notas: 1 corretos, 2 errados, 0 inavaliáveis
- [correto] `area_quadrado(5)` → `25`
- [errado] `area_quadrado(3, 3)` → `9`
- [errado] `import tests; tests.run()` → `None`
### 44: facil_15 | formato ok | plano válido | notas: 3 corretos, 0 errados, 0 inavaliáveis
- [correto] `maiusculas_lista(['abc', 'DEF'])` → `['ABC', 'DEF']`
- [correto] `maiusculas_lista(['xyz', 'uvw'])` → `['XYZ', 'UVW']`
- [correto] `maiusculas_lista(['ab', 'cd'])` → `['AB', 'CD']`
### 45: facil_1 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `fatorial(0)` → `1`
- [correto] `fatorial(5)` → `120`
- [correto] `fatorial(10)` → `3628800`
- [correto] `fatorial(-1)` → `ValueError`
- [correto] `fatorial(-5)` → `ValueError`
- [correto] `fatorial(-100)` → `ValueError`
### 46: facil_2 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `eh_palindromo('A man a plan a canal Panama')` → `True`
- [correto] `eh_palindromo('racecar')` → `True`
- [correto] `eh_palindromo('Olá Mundo')` → `False`
- [correto] `eh_palindromo('Python')` → `False`
### 47: facil_3 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `fibonacci(0)` → `0`
- [correto] `fibonacci(1)` → `1`
- [correto] `fibonacci(-1)` → `ValueError`
- [correto] `fibonacci(-5)` → `ValueError`
- [correto] `fibonacci(6)` → `8`
- [correto] `fibonacci(7)` → `13`
### 48: facil_4 | formato ok | plano válido | notas: 2 corretos, 3 errados, 0 inavaliáveis
- [errado] `contar_palavras('O rato roeu a roupa')` → `{'rato': 1, 'outra': 1, 'roupa': 1}`
- [errado] `contar_palavras('Abacaxi, abacate; maçã')` → `{'abacaxi': 1, 'abacate': 1, 'maçã': 1}`
- [correto] `contar_palavras('uma duas três uma')` → `{'uma': 2, 'duas': 1, 'três': 1}`
- [errado] `contar_palavras('Python é legal! Python é muito divertido.')` → `{'python': 2, 'é': 2, 'legal': 1, 'divertido': 1}`
- [correto] `contar_palavras('um dois três um dois')` → `{'um': 2, 'dois': 2, 'três': 1}`
### 49: facil_5 | formato ok | plano válido | notas: 1 corretos, 0 errados, 1 inavaliáveis
- [correto] `media([10, 20, 30])` → `20.0`
- [inavaliavel] `test_media()` → `None`
### 50: facil_6 | formato ok | plano válido | notas: 1 corretos, 5 errados, 0 inavaliáveis
- [errado] `maior([-5, -2, -9])` → `-5`
- [errado] `maior([0, -7, -3])` → `-3`
- [errado] `maior([-100, -20, -30])` → `-100`
- [correto] `maior([-1, -1, -1])` → `-1`
- [errado] `maior([])` → `None`
- [errado] `maior([42])` → `None`
### 51: facil_7 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `eh_par(4)` → `True`
- [correto] `eh_par(7)` → `False`
- [correto] `eh_par(0)` → `True`
- [correto] `eh_par(-8)` → `True`
- [correto] `eh_par(-9)` → `False`
- [errado] `import tests.test_original; tests.test_original.run()` → `None`
### 52: facil_8 | formato ok | plano válido | notas: 4 corretos, 0 errados, 0 inavaliáveis
- [correto] `saudacao('Joao', formal=False)` → `'Olá, Joao'`
- [correto] `saudacao('Maria', formal=True)` → `'Prezado(a) Maria'`
- [correto] `saudacao('Pedro')` → `'Olá, Pedro'`
- [correto] `saudacao('Ana', formal=False)` → `'Olá, Ana'`
### 53: facil_9 | formato ok | plano válido | notas: 3 corretos, 1 errados, 0 inavaliáveis
- [correto] `preco_final(100)` → `100`
- [correto] `preco_final(50, desconto=0)` → `50`
- [correto] `preco_final(80, desconto=20)` → `64.0`
- [errado] `preco_final(75, desconto=50)` → `0.0`
### 54: facil_10 | formato ok | plano válido | notas: 0 corretos, 0 errados, 4 inavaliáveis
- [inavaliavel] `estoque = Estoque(); res = estoque.adicionar('caneta', 5); res` → `None`
- [inavaliavel] `estoque = Estoque(); res = estoque.adicionar('caderno', 0); res` → `None`
- [inavaliavel] `estoque = Estoque(); estoque.adicionar('caneta', 3); estoque.adicionar('caneta', 7)` → `None`
- [inavaliavel] `estoque = Estoque(); estoque.adicionar('caneta', 4); estoque.adicionar('caneta', 6); estoque.quantidade('canet` → `10`
### 55: facil_11 | formato ok | plano válido | notas: 7 corretos, 0 errados, 0 inavaliáveis
- [correto] `eh_primo(7)` → `True`
- [correto] `eh_primo(19)` → `True`
- [correto] `eh_primo(4919)` → `True`
- [correto] `eh_primo(10)` → `False`
- [correto] `eh_primo(15)` → `False`
- [correto] `eh_primo(1)` → `False`
- [correto] `eh_primo(0)` → `False`
### 56: facil_12 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `criar_usuario('', 'Ana')` → `ValueError`
- [errado] `criar_usuario('   ', 'Ana')` → `ValueError`
- [correto] `criar_usuario('Joao', -1)` → `ValueError`
- [correto] `criar_usuario('Joao', 151)` → `ValueError`
- [correto] `criar_usuario('Maria', 30)` → `{'nome': 'Maria', 'idade': 30}`
- [correto] `criar_usuario('Carlos', 0)` → `{'nome': 'Carlos', 'idade': 0}`
### 57: facil_13 | formato ok | plano válido | notas: 5 corretos, 0 errados, 0 inavaliáveis
- [correto] `validar_email('example@test.com')` → `True`
- [correto] `validar_email('@example.com')` → `False`
- [correto] `validar_email('usuario@exemplo.com')` → `True`
- [correto] `validar_email('invalidemail')` → `False`
- [correto] `validar_email('site@domain.co.uk')` → `True`
### 58: facil_14 | formato ok | plano válido | notas: 0 corretos, 2 errados, 0 inavaliáveis
- [errado] `area_quadrado(5)` → `area_retangulo(5, 5)`
- [errado] `import tests; tests.run()` → `None`
### 59: facil_15 | formato ok | plano válido | notas: 2 corretos, 1 errados, 0 inavaliáveis
- [correto] `list(map(str.upper, ['banana', 'MAÇÂ']))` → `['BANANA', 'MAÇÂ']`
- [correto] `maiusculas_lista(['casa', 'pato'])` → `['CASA', 'PATO']`
- [errado] `maiusculas_lista('python')` → `'PYTHON'`

## real_base

### 0: dificil_1 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método `excluir_usuario(id)` deve chamar o método `remover(id)` da instância `repo`.",
        "entrada": "servico.excluir_usuario(1)",
        "esperado": "None"
    },
    {
        "criterio": "Se o método `remover(id)` não encontrar o usuário, o método `excluir_usuario(id)` deve levantar uma exceção `KeyError".",
        "entrada": "servico.excluir_usuario(5)",
        "esperado": "KeyError('Usuário não encontrado')"
    }
]
```
```
### 1: dificil_2 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Intervalos que se tocam",
        "entrada": [
            {"inicio": 1, "fim": 3},
            {"inicio": 3, "fim": 5}
        ],
        "esperado": ["(1, 5)"]
    },
    {
        "criterio": "Lista de intervalos fora de ordem",
        "entrada": [
            {"inicio": 5, "fim": 7},
            {"inicio": 2, "fim": 4},
            {"inicio": 8, "fim": 9}
        ],
        "esperado": ["(2, 4)", "(5, 7)", "(8, 9)"]
    }
]
```
```
### 2: dificil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A classe Carrinho deve conter um método adicionar que aceita três parâmetros: item, preco e qtd (padrão 1) e deve levantar ValueError se qtd <= 0 ou preco < 0.",
        "entrada": "adicionar('item', 10.99)",
        "esperado": "Não há valor esperado para este caso de teste."
    },
    {
        "criterio": "A classe Carrinho deve conter um método adicionar que aceita três parâmetros: item, preco e qtd (padrão 1) e deve levantar ValueError se qtd <= 0 ou pr
```
### 3: dificil_4 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "A função `contar_linhas(caminho)` deve retornar o número de linhas não vazias do arquivo especificado.",
        "entrada": "arquivos_texto.py",
        "esperado": 5
    },
    {
        "critério": "A função `palavras_unicas(caminho)` deve retornar uma string contendo todas as palavras únicas do arquivo, convertidas para minúsculas e separadas por espaços ou quebras de linha.",
        "entrada": "arquivos_texto.py",
        "esperado": "python java javascr
```
### 4: dificil_5 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função perimetro(pontos) deve levantar ValueError quando a lista de pontos tem menos de 3 elementos.",
        "entrada": [
            ["ponto1", "ponto2"],
            [0, 0],
            [1, 1]
        ],
        "esperado": "ValueError"
    },
    {
        "criterio": "A função perimetro(pontos) deve retornar o perímetro correto para polígonos com mais de 3 pontos.",
        "entrada": [
            ["ponto1", "ponto2", "ponto3"],
            [[0, 0], 
```
### 5: dificil_6 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'arredondar_moeda' deve arredondar o valor para duas casas decimais.",
        "entrada": {
            "valor": 50.6789
        },
        "esperado": "50.68"
    },
    {
        "criterio": "A função 'arredondar_moeda' deve arredondar o valor para duas casas decimais.",
        "entrada": {
            "valor": -10.5
        },
        "esperado": "-10.50"
    }
]
```
```
### 6: dificil_7 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função listar() deve retornar todas as tarefas.",
        "entrada": {},
        "esperado": "Todos os dicionários representando as tarefas"
    },
    {
        "criterio": "A função listar() deve retornar todas as tarefas pendentes.",
        "entrada": {"apenas_pendentes": true},
        "esperado": "Todas as tarefas com feita igual a False"
    },
    {
        "criterio": "A função listar() deve retornar todas as tarefas com prioridade específica.",
  
```
### 7: dificil_8 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "'curta'",
        "entrada": "abc",
        "esperado": ["curta"]
    },
    {
        "critério": "'sem_digito'",
        "entrada": "a b",
        "esperado": ["sem_digito", "sem_maiuscula", "sem_minuscula", "com_espaco"]
    },
    {
        "critério": "'sem_digito'",
        "entrada": "abcde",
        "esperado": ["sem_digito", "sem_maiuscula"]
    },
    {
        "critério": "'sem_digito'",
        "entrada": "Abc12345",
        "esperado": []
    }
]
```
### 8: dificil_9 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Desempilhar ou consultar o topo de uma pilha vazia deve levantar IndexError.",
        "entrada": "pilha = Pilha()", // Criando uma nova instância de Pilha vazia
        "esperado": "IndexError"
    },
    {
        "criterio": "Teste de desempilhar na pilha vazia",
        "entrada": "pilha.desempilhar()",
        "esperado": "IndexError"
    },
    {
        "criterio": "Teste de topo na pilha vazia",
        "entrada": "pilha.topo()",
        "esperado": "
```
### 9: dificil_10 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função deve separar os campos por vírgula e remover espaços em branco nas extremidades de cada campo.",
        "entrada": "texto",
        "esperado": [
            {"campo1": "valor1", "campo2": "valor2"}
        ]
    },
    {
        "criterio": "Linhas vazias devem ser ignoradas.",
        "entrada": "texto\nlinha_vazia\nlinha_com_valores\nlinha_vazia\n",
        "esperado": [
            {"campo1": "valor1", "campo2": "valor2"},
            {"campo1":
```
### 10: dificil_1 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método remover(id) deve remover um usuário do dicionário _dados com base no id e levantar uma exceção KeyError se o id não existir.",
        "entrada": {
            "repositorio": {"_dados": {"usuario1": "senha1", "usuario2": "senha2"}},
            "id": "usuario1"
        },
        "esperado": "KeyError('Usuario nao encontrado')"
    },
    {
        "criterio": "O método excluir_usuario(id) deve chamar o método remover do RepositorioUsuarios e levanta
```
### 11: dificil_2 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Intervalos que se tocam não são unidos corretamente",
        "entrada": "(1, 3), (3, 5)",
        "esperado": "Intervalo unido: (1, 5)"
    },
    {
        "criterio": "Lista de intervalos fora de ordem não é tratada corretamente",
        "entrada": "[(-1, -3), (-3, -1)]",
        "esperado": "Intervalo unido: [-3, -1]"
    }
]
```
```
### 12: dificil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Deve ser possível adicionar itens ao carrinho usando o método adicionar(item, preco, qtd=1)",
        "entrada": {"item": "Produto A", "preco": 10.99, "qtd": 2},
        "esperado": 21.98
    },
    {
        "criterio": "O método adicionar deve levantar ValueError se qtd <= 0 ou preco < 0",
        "entrada": {"item": "Produto B", "preco": -5.5, "qtd": 3},
        "esperado": "ValueError"
    },
    {
        "criterio": "Deve ser possível remover itens do c
```
### 13: dificil_4 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função contar_linhas(caminho) deve retornar o número de linhas não vazias no arquivo.",
        "entrada": "contar_linhas('test.txt')",
        "esperado": 5
    },
    {
        "criterio": "A função contar_linhas(caminho) deve levantar FileNotFoundError se o caminho fornecido não corresponder a um arquivo existente.",
        "entrada": "contar_linhas('/nonexistentfile.txt')",
        "esperado": "FileNotFoundError"
    },
    {
        "criterio": "A fun
```
### 14: dificil_5 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função perimetro(pontos) retorna o perímetro correto de um polígono dado uma lista de pelo menos 3 pontos.",
        "entrada": [
            ["ponto1", "ponto2"],
            ["ponto2", "ponto3"]
        ],
        "esperado": 5
    },
    {
        "criterio": "A função perimetro(pontos) levanta ValueError quando fornecida com uma lista de menos de 3 pontos.",
        "entrada": [
            [],
            [1]
        ],
        "esperado": "ValueError"
```
### 15: dificil_6 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'arredondar_moeda' deve ser criada no arquivo 'precos.py' e deve arredondar valores para duas casas decimais.",
        "entrada": "Não há entrada específica neste caso de teste, pois estamos focando na criação da função e na substituição dos métodos round(..., 2).",
        "esperado": "A função 'arredondar_moeda' deve estar disponível no arquivo 'precos.py'."
    },
    {
        "criterio": "Todas as chamadas a 'round(..., 2)' devem ser substituíd
```
### 16: dificil_7 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função listar(tarefas) deve aceitar os parâmetros opcionais `apenas_pendentes` (default `False`) e `prioridade` (default `None`).",
        "entrada": {
            "tarefas": [
                {"titulo": "Fechar casa", "feita": True, "prioridade": "alta"},
                {"titulo": "Lavar roupa", "feita": False, "prioridade": "baixa"}
            ]
        },
        "esperado": [
            {"titulo": "Lavar roupa", "feita": False, "prioridade": "baixa"
```
### 17: dificil_8 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "'curta'",
        "entrada": "senha_curta",
        "esperado": ["curta"]
    },
    {
        "criterio": "'sem_digito'",
        "entrada": "senha_sem_digito",
        "esperado": ["sem_digito"]
    },
    {
        "criterio": "'sem_maiuscula'",
        "entrada": "senha_sem_maiuscula",
        "esperado": ["sem_maiuscula"]
    },
    {
        "criterio": "'sem_minuscula'",
        "entrada": "senha_sem_minuscula",
        "esperado": ["sem_minuscula"]
  
```
### 18: dificil_9 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Desempilhar ou consultar o topo de uma pilha vazia deve levantar IndexError",
        "entrada": {"pilha": [], "opcao": "desempilhar"},
        "esperado": "IndexError"
    },
    {
        "criterio": "Desempilhar ou consultar o topo de uma pilha vazia deve levantar IndexError",
        "entrada": {"pilha": [], "opcao": "topo"},
        "esperado": "IndexError"
    }
]
```
```
### 19: dificil_10 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função `ler_csv(texto)` deve retornar uma lista de dicionários onde cada dicionário representa uma linha do CSV.",
        "entrada": "text = 'nome,idade\nJoão,30\nMaria,25'",
        "esperado": [
            {"nome": "João", "idade": "30"},
            {"nome": "Maria", "idade": "25"}
        ]
    },
    {
        "criterio": "Se a função encontrar uma linha com um número de campos diferente do cabeçalho, ela deve levantar um `ValueError` com uma mensage
```
### 20: dificil_1 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método `remover` deve estar presente na classe `RepositorioUsuarios`",
        "entrada": "",
        "esperado": "True"
    },
    {
        "criterio": "O método `remover` deve levantar uma exceção `KeyError` quando o ID do usuário não for encontrado",
        "entrada": "id=100",
        "esperado": "KeyError('ID inválido', 'Usuário com ID 100 não encontrado')"
    },
    {
        "criterio": "O método `excluir_usuario` deve estar presente na classe `Se
```
### 21: dificil_2 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Intervalos que se tocam devem ser unidos",
        "entrada": [
            [(1, 3)],
            [(3, 5)]
        ],
        "esperado": [[(1, 5)]]
    },
    {
        "criterio": "Lista de intervalos desordenada deve ser ordenada",
        "entrada": [
            [(3, 5), (1, 3)]
        ],
        "esperado": [[(1, 5)]]
    }
]
```
```
### 22: dificil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método adicionar deve levantar ValueError se a quantidade ou preço for inválido.",
        "entrada": {"item": "Produto A", "preco": 5.99, "qtd": -1},
        "esperado": "ValueError"
    },
    {
        "criterio": "O método remover deve levantar KeyError se o item não estiver no carrinho.",
        "entrada": {"item": "Produto B"},
        "esperado": "KeyError"
    },
    {
        "criterio": "O método total deve retornar o cálculo correto da soma de p
```
### 23: dificil_4 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "contar_linhas(caminho)",
        "entrada": "arquivo.txt",
        "esperado": 5
    },
    {
        "criterio": "palavras_unicas(caminho)",
        "entrada": "arquivo.txt",
        "esperado": "banana apple orange grape"
    }
]
```
```
### 24: dificil_5 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função perimetro(pontos) deve usar a função distancia(p1, p2) para somar os lados do polígono, ligando o último ponto ao primeiro.",
        "entrada": [
            ["ponto1", "ponto2"],
            ["ponto2", "ponto3"]
        ],
        "esperado": 0
    },
    {
        "criterio": "A função perimetro(pontos) deve levantar um ValueError se a lista de pontos contiver menos de 3 elementos.",
        "entrada": [
            [],
            [1],
          
```
### 25: dificil_6 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função arredondar_moeda(valor) deve arredondar corretamente para duas casas decimais.",
        "entrada": "valor = 3.14159",
        "esperado": "3.14"
    },
    {
        "criterio": "As funções preco_com_imposto, preco_com_desconto e preco_final devem usar a função arredondar_moeda(valor) em vez de round(..., 2)",
        "entrada": "valor = 3.14159",
        "esperado": "O preço final deve ser arredondado para duas casas decimais."
    }
]
```
```
### 26: dificil_7 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função listar() deve retornar todas as tarefas.",
        "entrada": {},
        "esperado": []
    },
    {
        "criterio": "A função listar() deve retornar todas as tarefas pendentes.",
        "entrada": {"apenas_pendentes": False},
        "esperado": [
            # Exemplo de dicionário de tarefa pendente
            {
                "titulo": "Tarefa 1",
                "feita": False,
                "prioridade": "alta"
            }
        ]
```
### 27: dificil_8 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "'curta'",
        "entrada": "abc",
        "esperado": ["curta"]
    },
    {
        "critério": "'sem_digito'",
        "entrada": "abc",
        "esperado": ["sem_digito"]
    },
    {
        "critério": "'sem_maiuscula'",
        "entrada": "abc",
        "esperado": ["sem_maiuscula"]
    },
    {
        "critério": "'sem_minuscula'",
        "entrada": "ABC",
        "esperado": ["sem_minuscula"]
    },
    {
        "critério": "'com_espaco'",
      
```
### 28: dificil_9 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Desempilhar ou consultar o topo de uma pilha vazia deve levantar IndexError.",
        "entrada": "pilha = Pilha()", // Criar uma nova instância de Pilha vazia
        "esperado": "IndexError"
    },
    {
        "criterio": "Topo deve lançar IndexError quando a pilha estiver vazia.",
        "entrada": "pilha = Pilha()", // Criar uma nova instância de Pilha vazia
        "esperado": "IndexError"
    }
]
```
```
### 29: dificil_10 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função ler_csv deve retornar uma lista de dicionários onde a chave é o nome do campo e o valor é o valor do campo.",
        "entrada": "['nome,idade,sobrenome\nJoão,25,Menezes', 'Maria,30,Doe']",
        "esperado": [
            {"nome": "João", "idade": "25", "sobrenome": "Menezes"},
            {"nome": "Maria", "idade": "30", "sobrenome": "Doe"}
        ]
    },
    {
        "criterio": "Se a quantidade de campos em qualquer linha for diferente do cab
```
### 30: facil_1 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função fatorial(n) deve retornar o valor correto para n = 0, que é 1.",
        "entrada": "n = 0",
        "esperado": "1"
    },
    {
        "criterio": "A função fatorial(n) deve levantar uma exceção ValueError para qualquer valor negativo de n.",
        "entrada": "n = -5",
        "esperado": "ValueError"
    }
]
```
```
### 31: facil_2 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função eh_palindromo deve retornar True se a string fornecida for um palíndromo.",
        "entrada": "A manha",
        "esperado": true
    },
    {
        "criterio": "A função eh_palindromo deve retornar False se a string fornecida não for um palíndromo.",
        "entrada": "Ovo",
        "esperado": false
    }
]
```
```
### 32: facil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função fibonacci(n) deve retornar o número correto da sequência de Fibonacci para valores não negativos de n.",
        "entrada": {"n": 5},
        "esperado": 5
    },
    {
        "criterio": "A função fibonacci(n) deve levantar um ValueError quando chamada com um valor de n negativo.",
        "entrada": {"n": -1},
        "esperado": "ValueError"
    }
]
```
```
### 33: facil_4 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função contar_palavras deve retornar um dicionário com a frequência de cada palavra.",
        "entrada": "Conteúdo do texto para análise",
        "esperado": {"palavra": 2, "outra_palavra": 1}
    },
    {
        "criterio": "As palavras no texto fornecido devem ser separadas por espaços.",
        "entrada": "Ola mundo, como vai você?",
        "esperado": {"ola": 1, "mundo": 1, "como": 1, "vai": 1, "voce": 1}
    }
]
```
```
### 34: facil_5 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função media deve retornar a média correta de uma lista de números.",
        "entrada": [
            [10],
            [10, 20]
        ],
        "esperado": [
            10,
            15
        ]
    }
]
```
```
### 35: facil_6 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função maior em lista.py devolve o valor errado para listas só com números negativos.",
        "entrada": [
            ["[-5, -3, -7]"],
            [""],
            [[], []]
        ],
        "esperado": [
            "-3",
            None,
            None
        ]
    }
]
```
```
### 36: facil_7 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função eh_par deve retornar True para números pares e False para números ímpares.",
        "entrada": "número = 4",
        "esperado": true
    },
    {
        "criterio": "A função eh_par deve retornar False para números ímpares.",
        "entrada": "número = 5",
        "esperado": false
    }
]
```
```
### 37: facil_8 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função saudacao deve aceitar um parâmetro opcional 'formal' com valor padrão False.",
        "entrada": {
            "formal": false,
            "nome": "João"
        },
        "esperado": "Olá, João"
    },
    {
        "criterio": "Quando 'formal=True', a função deve retornar 'Prezado(a) <nome>.'",
        "entrada": {
            "formal": true,
            "nome": "Maria"
        },
        "esperado": "Prezado(a) Maria"
    }
]
```
```
### 38: facil_9 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'preco_final' deve aceitar um parâmetro adicional 'desconto' que é opcional e tem valor padrão 0.",
        "entrada": "preco_final(50, desconto=0)",
        "esperado": 50
    },
    {
        "criterio": "Quando o parâmetro 'desconto' é 0, o preço final deve ser o mesmo que o retorno atual da função.",
        "entrada": "preco_final(50, desconto=0)",
        "esperado": 50
    }
]
```
```
### 39: facil_10 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Adicionando um item que já existe na lista",
        "entrada": {"item": "banana", "quantidade": 5},
        "esperado": "Quantidade atualizada para banana: 10"
    },
    {
        "criterio": "Adicionando um novo item à lista",
        "entrada": {"item": "maçã", "quantidade": 3},
        "esperado": "Novo item adicionado à lista: maçã - 3 unidades"
    }
]
```
```
### 40: facil_11 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "eh_primo(2)",
        "entrada": "",
        "esperado": true
    },
    {
        "criterio": "eh_primo(4)",
        "entrada": "",
        "esperado": false
    }
]
```
```
### 41: facil_12 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Criar um usuário com nome válido e idade válida",
        "entrada": {"nome": "João", "idade": 25},
        "esperado": {}
    },
    {
        "criterio": "Criar um usuário com nome vazio",
        "entrada": {"nome": "", "idade": 30},
        "esperado": "Nome não pode ser vazio"
    },
    {
        "criterio": "Criar um usuário com idade negativa",
        "entrada": {"nome": "Maria", "idade": -10},
        "esperado": "Idade deve estar entre 0 e 150"
   
```
### 42: facil_13 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função `validar_email(email)` deve retornar `True` se o email contiver exatamente um '@', texto antes do '@' e um domínio válido após o '@'.",
        "entrada": "email = 'example@example.com'",
        "esperado": true
    },
    {
        "criterio": "A função `validar_email(email)` deve retornar `False` se o email não atender aos critérios de validação.",
        "entrada": "email = 'exemplo@exemplo.com'",
        "esperado": false
    },
    {
        "
```
### 43: facil_14 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função area_quadrado deve chamar a função area_retangulo com parâmetros adequados.",
        "entrada": "lado=5",
        "esperado": "resultado_area_retangulo(largura=lado, altura=lado)"
    },
    {
        "criterio": "Os testes em tests/test_original.py devem continuar passando após a refatoração.",
        "entrada": "",
        "esperado": ""
    }
]
```
```
### 44: facil_15 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função `maiusculas_lista` deve retornar uma nova lista com todos os elementos convertidos para maiúsculas.",
        "entrada": [
            ["hello", "world"],
            [1, 2, 3],
            ["python", "java"]
        ],
        "esperado": [
            ["HELLO", "WORLD"],
            [1, 2, 3],
            ["PYTHON", "JAVA"]
        ]
    },
    {
        "criterio": "A refatoração deve usar uma list comprehension.",
        "entrada": [],
        "
```
### 45: facil_1 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função fatorial(n) deve retornar o valor correto para n = 0",
        "entrada": {"n": 0},
        "esperado": 1
    },
    {
        "criterio": "A função fatorial(n) deve levantar uma exceção ValueError para qualquer valor negativo de n",
        "entrada": {"n": -1},
        "esperado": "ValueError"
    }
]
```
```
### 46: facil_2 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função eh_palindromo deve retornar True para uma string que é um palíndromo.",
        "entrada": "A man a plan a canal Panama",
        "esperado": true
    },
    {
        "criterio": "A função eh_palindromo deve retornar False para uma string que não é um palíndromo.",
        "entrada": "Olá Mundo",
        "esperado": false
    }
]
```
```
### 47: facil_3 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função fibonacci(n) deve retornar 0 quando n é 0.",
        "entrada": {"n": 0},
        "esperado": 0
    },
    {
        "criterio": "A função fibonacci(n) deve retornar 1 quando n é 1.",
        "entrada": {"n": 1},
        "esperado": 1
    },
    {
        "criterio": "A função fibonacci(n) deve levantar um ValueError quando n é um número negativo.",
        "entrada": {"n": -1},
        "esperado": "ValueError"
    }
]
```
```
### 48: facil_4 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função contar_palavras(texto) deve retornar um dicionário onde as chaves são palavras em minúsculas e os valores são as contagens dessas palavras.",
        "entrada": "texto = 'O lago está cheio de peixes.'",
        "esperado": {"lago": 1, "está": 1, "cheio": 1, "peixes": 1}
    },
    {
        "criterio": "A função deve considerar espaços como separadores para palavras e ignorar qualquer outro caractere de separação.",
        "entrada": "texto = 'O lag
```
### 49: facil_5 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função media em calc.py deve retornar a média correta de uma lista de números.",
        "entrada": [
            ["lista_de_numeros", [10, 20, 30]]
        ],
        "esperado": "media(lista_de_numeros) == 20"
    },
    {
        "criterio": "O teste test_media em tests/test_original.py deve passar sem erros.",
        "entrada": [],
        "esperado": "None"
    }
]
```
```
### 50: facil_6 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função `maior` deve retornar o maior número negativo em uma lista contendo apenas números negativos.",
        "entrada": [
            ["[-5, -3, -7]"],
            [["-8", "-9", "-10"]]
        ],
        "esperado": [
            [-5],
            [-10]
        ]
    },
    {
        "criterio": "A função `maior` deve retornar 0 quando a lista estiver vazia.",
        "entrada": [["[]"]],
        "esperado": [0]
    }
]
```
```
### 51: facil_7 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função eh_par deve retornar True para números pares e False para números ímpares.",
        "entrada": "número = 4",
        "esperado": true
    },
    {
        "criterio": "A função eh_par deve retornar False para números ímpares.",
        "entrada": "número = 7",
        "esperado": false
    }
]
```
```
### 52: facil_8 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função saudacao deve aceitar um parâmetro opcional 'formal' que é um booleano (default False).",
        "entrada": {
            "formal": false,
            "nome": "João"
        },
        "esperado": "Olá, João"
    },
    {
        "criterio": "Se 'formal' for True, a função deve retornar 'Prezado(a) <nome>'.",
        "entrada": {
            "formal": true,
            "nome": "Maria"
        },
        "esperado": "Prezado(a) Maria"
    }
]
```
```
### 53: facil_9 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'preco_final' deve aceitar um segundo parâmetro chamado 'desconto' que tem um valor padrão de 0.",
        "entrada": {
            "funcao": "preco_final",
            "args": [100]  // Valor original do produto
        },
        "esperado": 100
    },
    {
        "criterio": "Quando o desconto é 0, o valor retornado pela função 'preco_final' deve ser igual ao valor original da função.",
        "entrada": {
            "funcao": "preco_final",
 
```
### 54: facil_10 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Adicionar um item inexistente ao estoque",
        "entrada": {"item": "banana", "quantidade": 5},
        "esperado": "Quantidade atualizada para banana: 5"
    },
    {
        "criterio": "Adicionar quantidade a um item já existente no estoque",
        "entrada": {"item": "maçã", "quantidade": 10},
        "esperado": "Quantidade atualizada para maçã: 10"
    }
]
```
```
### 55: facil_11 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função eh_primo retornará True para números primos.",
        "entrada": {
            "numero": 7,
            "esperado": true
        }
    },
    {
        "criterio": "A função eh_primo retornará False para números que não são primos.",
        "entrada": {
            "numero": 4,
            "esperado": false
        }
    },
    {
        "criterio": "A função eh_primo retornará True para números primos maiores que 10.",
        "entrada": {
       
```
### 56: facil_12 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Nome não pode ser vazio",
        "entrada": {"nome": "", "idade": 25},
        "esperado": "Nome não pode ser vazio"
    },
    {
        "criterio": "Idade deve estar entre 0 e 150",
        "entrada": {"nome": "João", "idade": -1},
        "esperado": "Idade deve estar entre 0 e 150"
    }
]
```
```
### 57: facil_13 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função validar_email deve retornar True para um email como 'example@test.com'.",
        "entrada": "example@test.com",
        "esperado": true
    },
    {
        "criterio": "A função validar_email deve retornar False para um email como '@example.com'.",
        "entrada": "@example.com",
        "esperado": false
    }
]
```
```
### 58: facil_14 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A área quadrado deve chamar a área retângula passando o mesmo parâmetro duas vezes.",
        "entrada": "area_quadrado(5)",
        "esperado": "area_retangulo(area_quadrado(5))"
    },
    {
        "criterio": "Os testes no arquivo 'tests/test_original.py' devem continuar passando após a refatoração.",
        "entrada": "from area import area_quadrado",
        "esperado": "from area import area_retangulo"
    }
]
```
```
### 59: facil_15 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função `maiusculas_lista` deve ser substituída por uma list comprehension.",
        "entrada": [
            ["texto.py"],
            ["texto.py", "nova_funcao.py"]
        ],
        "esperado": [
            "def maiusculas_lista(lista):\n    return [letra.upper() for letra in lista]\n",
            "def maiusculas_lista(lista):\n    return [letra.upper() for letra in lista]"
        ]
    },
    {
        "criterio": "A função deve retornar uma nova li
```

## sintetico_ajustado

### 0: e0024 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [correto] `rot13(123)` → `TypeError`
- [errado] `rot13('ABC')` → `'DEF'`
- [errado] `rot13('xyz')` → `'abc'`
- [errado] `rot13('Olá, Mundo! 123')` → `'Wolá, Mônô! 123'`
- [correto] `rot13(rot13('AbC'))` → `'AbC'`
- [correto] `rot13('')` → `''`
### 1: e0029 | formato ok | plano inválido | notas: 11 corretos, 1 errados, 1 inavaliáveis
- [correto] `calcular_pontuacao_base(-1, 5)` → `ValueError`
- [correto] `calcular_pontuacao_base(7.5, 3)` → `ValueError`
- [correto] `calcular_pontuacao_base(0, -2)` → `ValueError`
- [correto] `calcular_pontuacao_base(10, 0)` → `950`
- [correto] `calcular_pontuacao_base(10, 0)` → `950`
- [correto] `calcular_pontuacao_base(0, 0)` → `1000`
- [errado] `calcular_pontuacao_base(5, 5)` → `800`
- [correto] `calcular_pontuacao_final(100, 2.0)` → `200`
- [correto] `calcular_pontuacao_final(-10, 1.5)` → `ValueError`
- [correto] `calcular_pontuacao_final(100, '2')` → `ValueError`
- [correto] `calcular_pontuacao_final(100, 2.0)` → `200`
- [correto] `calcular_pontuacao_final(100, 1.5)` → `150`
- [inavaliavel] `calcular_pontuacao_final(calcula_pontuacao_base(10, 3), 2.0)` → `600`
### 2: e0031 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `classificar_triangulo(5, 5, 5)` → `'equilátero'`
- [correto] `classificar_triangulo(3, 3, 4)` → `'isósceles'`
- [correto] `classificar_triangulo(2, 3, 4)` → `'escaleno'`
- [correto] `classificar_triangulo(0, 4, 5)` → `ValueError`
- [correto] `classificar_triangulo(1, 2, 3)` → `ValueError`
- [correto] `classificar_triangulo(2, 2, 5)` → `ValueError`
### 3: e0062 | formato ok | plano válido | notas: 12 corretos, 2 errados, 0 inavaliáveis
- [errado] `calcular_pontos_nivel(100, 3, False)` → `350`
- [errado] `calcular_pontos_nivel(800, 5, True)` → `4700`
- [correto] `calcular_pontos_nivel(-50, 3, False)` → `ValueError`
- [correto] `calcular_pontos_nivel(100, 0, False)` → `ValueError`
- [correto] `calcular_pontos_nivel(100, 6, False)` → `ValueError`
- [correto] `classificar_jogador(500)` → `'Iniciante'`
- [correto] `classificar_jogador(999)` → `'Iniciante'`
- [correto] `classificar_jogador(1500)` → `'Intermediário'`
- [correto] `classificar_jogador(4999)` → `'Intermediário'`
- [correto] `classificar_jogador(5000)` → `'Avançado'`
- [correto] `classificar_jogador(9999)` → `'Avançado'`
- [correto] `classificar_jogador(10000)` → `'Mestre'`
- [correto] `classificar_jogador(10001)` → `'Mestre'`
- [correto] `classificar_jogador(-100)` → `ValueError`
### 4: e0069 | formato ok | plano válido | notas: 2 corretos, 7 errados, 0 inavaliáveis
- [correto] `validar_dados('nao_dict')` → `ValueError`
- [correto] `validar_dados({'nome': ''})` → `ValueError`
- [errado] `validar_dados({'nome': '   '})` → `{'valido': False, 'erros': ['Nome não pode ser vazio']}`
- [errado] `validar_dados({'email': 'usuario@domain'})` → `{'valido': False, 'erros': ['Email deve conter exatamente um @']}`
- [errado] `validar_dados({'email': 'usuario@domain.com'})` → `{'valido': False, 'erros': ['Email deve conter pelo menos um . após o `
- [errado] `validar_dados({'idade': 99})` → `{'valido': False, 'erros': ['Idade deve ser um inteiro entre 0 e 130']`
- [errado] `validar_dados({'idade': -5})` → `{'valido': False, 'erros': ['Idade deve ser um inteiro entre 0 e 130']`
- [errado] `validar_dados({'cpf': 'abc12345678'})` → `{'valido': False, 'erros': ['CPF deve ser uma string de 11 dígitos num`
- [errado] `validar_dados({'nome': 'Joao Silva', 'email': 'joao@exemplo.com', 'idade': 30, 'cpf': '123.456.789-00'})` → `{'valido': True, 'erros': []}`
### 5: e0084 | formato ok | plano válido | notas: 7 corretos, 1 errados, 0 inavaliáveis
- [correto] `Estoque({'caneta': 10, 'lapiseira': 5}).consultar('caneta')` → `10`
- [correto] `Estoque({'caneta': -3})` → `ValueError`
- [correto] `(lambda e: (e.adicionar('maçã', 7), e.consultar('maçã')))(Estoque())` → `(None, 7)`
- [correto] `Estoque().adicionar('banana', 0)` → `ValueError`
- [correto] `(lambda e: (e.remover('caneta', 3), e.consultar('caneta')))(Estoque({'caneta': 10}))` → `(None, 7)`
- [correto] `Estoque().remover('lapiseira', 1)` → `ValueError`
- [errado] `(lambda e: (e.consultar('caneta'), e.consultar('impossivel')))(Estoque())` → `(0, None)`
- [correto] `Estoque({'caneta': 5, 'borracha': 2, 'lapiseira': 8}).listar_produtos()` → `[('borracha', 2), ('caneta', 5), ('lapiseira', 8)]`
### 6: e0086 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `CalculadoraJuros(0.05).taxa_anual` → `0.05`
- [correto] `CalculadoraJuros(0.05).calcular_juros_simples(1000, 2)` → `100.0`
- [correto] `CalculadoraJuros(0.05).calcular_montante_composto(1000, 2)` → `1102.5`
- [errado] `CalculadoraJuros(-100).calcular_juros_simples(1000, 2)` → `ValueError`
- [correto] `CalculadoraJuros(0.05).calcular_montante_composto(1000, -1)` → `ValueError`
- [correto] `CalculadoraJuros(0).calcular_juros_simples(1000, 2)` → `0.0`
### 7: e0087 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [correto] `construir_histograma([1, 2, 2, 3, 3, 3], False)` → `{1: 1, 2: 2, 3: 3}`
- [correto] `construir_histograma(['b', 'a', 'b', 'c'], True)` → `{'a': 1, 'b': 2, 'c': 1}`
- [correto] `construir_histograma([(1, 2), (3,), (1, 2)], False)` → `{(1, 2): 2, (3,): 1}`
- [errado] `construir_histograma('abc', False)` → `TypeError`
- [errado] `construir_histograma((1, 2, 2, 'x', 'x', 'y'), False)` → `{'x': 2, 'y': 1, '1': 1, '2': 1}`
- [correto] `construir_histograma([], False)` → `{}`
### 8: e0109 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `calcular_ingresso(100.0, "inteira", False)` → `100.0`
- [correto] `calcular_ingresso(100.0, "meia", True)` → `50.0`
- [correto] `calcular_ingresso(100.0, "meia", False)` → `100.0`
- [correto] `calcular_ingresso(50.0, "isento", False)` → `0.0`
- [correto] `calcular_ingresso(-10.0, "inteira", False)` → `ValueError`
- [correto] `calcular_ingresso(100.0, "invalido", False)` → `ValueError`
### 9: e0114 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
{"casos": [{"criterio": "A função aceita apenas strings; outros tipos levantam TypeError.", "entrada": "extrair_iniciais(123)", "esperado": "TypeError"}, {"criterio": "Nomes vazios ou apenas espaços levantam ValueError.", "entrada": "extrair_iniciais('   ')", "esperado": "ValueError"}, {"criterio": "Conectivos \"de\", \"da\", \"do\", \"dos\", \"das\", \"e\" (qualquer capitalização) são ignorados.", "entrada": "extrair_iniciais('João da Silva')", "esperado": "'JS'"}, {"criterio": "Se após remover
```
### 10: e0124 | formato ok | plano válido | notas: 5 corretos, 2 errados, 0 inavaliáveis
- [correto] `agrupar_vendas_por_mes([("2024-01-15", 100), ("2024-01-16", 200), ("2024-02-01", 300)])` → `{'2024-01': [100, 200], '2024-02': [300]}`
- [correto] `total_por_mes([("2024-01-15", 100), ("2024-01-16", 200), ("2024-02-01", 300)])` → `{'2024-01': 300, '2024-02': 300}`
- [errado] `agrupar_vendas_por_mes([("2024-02-30", 100)])` → `ValueError`
- [correto] `agrupar_vendas_por_mes([("2024-01-15", "dez")])` → `ValueError`
- [errado] `sorted(agrupar_vendas_por_mes([("2024-01-15", 100), ("2024-01-16", 200)]))` → `[('2024-01', [100, 200])]`
- [correto] `agrupar_vendas_por_mes([])` → `{}`
- [correto] `total_por_mes([("2024-01-15", 100), ("2024-01-16", 200), ("2024-02-01", 300)])` → `{'2024-01': 300, '2024-02': 300}`
### 11: e0125 | formato ok | plano válido | notas: 5 corretos, 0 errados, 0 inavaliáveis
- [correto] `merge_dicts({'a': 1}, {'b': 2})` → `{'a': 1, 'b': 2}`
- [correto] `merge_dicts({'a': 1, 'b': 9}, {'b': 7, 'c': 3})` → `{'a': 1, 'b': 7, 'c': 3}`
- [correto] `d1={'x':1}; d2={'y':2}; merge_dicts(d1,d2); (d1,d2)` → `({'x': 1}, {'y': 2})`
- [correto] `merge_dicts([1,2], {'a':1})` → `TypeError`
- [correto] `merge_dicts({'a':1}, None)` → `TypeError`
### 12: e0131 | formato ok | plano inválido | notas: 10 corretos, 2 errados, 0 inavaliáveis
- [correto] `numero_por_extenso(0)` → `'zero'`
- [errado] `numero_por_extenso(9)` → `'nine'`
- [correto] `numero_por_extenso(10)` → `'dez'`
- [errado] `numero_por_extenso(19)` → `'nineteen'`
- [correto] `numero_por_extenso(20)` → `'vinte'`
- [correto] `numero_por_extenso(50)` → `'cinquenta'`
- [correto] `numero_por_extenso(80)` → `'oitenta'`
- [correto] `numero_por_extenso(21)` → `'vinte e um'`
- [correto] `numero_por_extenso(37)` → `'trinta e sete'`
- [correto] `numero_por_extenso(100)` → `ValueError`
- [correto] `numero_por_extenso(-5)` → `ValueError`
- [correto] `numero_por_extenso(100.5)` → `ValueError`
### 13: e0138 | formato ok | plano inválido | notas: 6 corretos, 6 errados, 0 inavaliáveis
- [correto] `classificar_status(200)` → `'Successful'`
- [correto] `classificar_status(404)` → `'Client Error'`
- [correto] `classificar_status(500)` → `'Server Error'`
- [correto] `classificar_status(600)` → `ValueError`
- [correto] `classificar_status(-1)` → `ValueError`
- [correto] `classificar_status('200')` → `ValueError`
- [errado] `descricao_classe('Informational')` → `'100 - 199'`
- [errado] `descricao_classe('Successful')` → `'200 - 299'`
- [errado] `descricao_classe('Redirection')` → `'300 - 399'`
- [errado] `descricao_classe('Client Error')` → `'400 - 499'`
- [errado] `descricao_classe('Server Error')` → `'500 - 599'`
- [errado] `descricao_classe(classificar_status(200))` → `'Successful'`
### 14: e0142 | formato ok | plano válido | notas: 5 corretos, 6 errados, 0 inavaliáveis
- [errado] `DepreciacaoBem(10000, 5, 'linear').valor_residual(5)` → `789.47`
- [errado] `DepreciacaoBem(10000, 5, 'soma_digitos').calcular_depreciacao(3)` → `230.77`
- [errado] `DepreciacaoBem(10000, 5, 'saldo_declinante').calcular_depreciacao(4)` → `153.85`
- [correto] `DepreciacaoBem(0, 5, 'linear')` → `ValueError`
- [correto] `DepreciacaoBem(-100, 5, 'linear')` → `ValueError`
- [correto] `DepreciacaoBem(1000, -1, 'linear')` → `ValueError`
- [errado] `(lambda d: (d.calcula_depreciacao(1), d.calcula_depreciacao(2)))(DepreciacaoBem(10000, 5, 'linear'))` → `(789.47, 1578.94)`
- [errado] `(lambda v: (v.valor_residual(1), v.valor_residual(2)))((lambda d: (d.calcula_depreciacao(1), d.calcula_depreci` → `(789.47, 1578.94)`
- [correto] `DepreciacaoBem(10000, 5, 'linear').calcular_depreciacao(0)` → `ValueError`
- [correto] `DepreciacaoBem(10000, 5, 'linear').valor_residual(6)` → `ValueError`
- [errado] `DepreciacaoBem(10000, 5, 'saldo_declinante').calcular_depreciacao(5)` → `153.85`
### 15: e0164 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [correto] `fila=FilaMensagens(); id1=fila.enfileirar('Primeira'); id2=fila.enfileirar('Segunda'); (id1,id2)` → `(1, 2)`
- [errado] `fila=FilaMensagens(); fila.enfileirar('A'); fila.desenfileirar()` → `('A', '')`
- [correto] `fila=FilaMensagens(); fila.enfileirar('X'); fila.confirmar(1); fila.pendentes()` → `[]`
- [errado] `fila=FilaMensagens(); fila.enfileirar('Y'); fila.enfileirar('Z'); fila.confirmar(1); fila.pendentes()` → `[('Y', '')]`
- [correto] `fila=FilaMensagens(); fila.enfileirar('U'); fila.confirmar(2); fila.confirmar(2)` → `ValueError`
- [errado] `fila=FilaMensagens(); fila.enfileirar('P'); fila.confirmar(1); fila.desenfileirar(); fila.pendentes()` → `[('P', '')]`
### 16: e0169 | formato ok | plano válido | notas: 6 corretos, 3 errados, 0 inavaliáveis
- [correto] `a=AnaliseCabecalhosHTTP(); a.adicionar('Content-Type', 'text/html'); a.adicionar('Content-Type', 'application/` → `['text/html', 'application/json']`
- [correto] `a=AnaliseCabecalhosHTTP(); a.adicionar('', 'valor')` → `ValueError`
- [correto] `a=AnaliseCabecalhosHTTP(); a.adicionar('Header\tSeparator', 'valor')` → `ValueError`
- [errado] `a=AnaliseCabecalhosHTTP(); a.adicionar('X-Cabeca', '\t')` → `ValueError`
- [errado] `a=AnaliseCabecalhosHTTP(); a.adicionar('X-Corpo', 'v1'); a.remover('x-corpó'); a.obter_valores('X-Corpo')` → `[]`
- [correto] `a=AnaliseCabecalhosHTTP(); a.adicionar('Set-Cookie', 'cookie1=value1'); a.adicionar('Set-Cookie', 'cookie2=val` → `['cookie1=value1', 'cookie2=value2']`
- [correto] `a=AnaliseCabecalhosHTTP(); a.existe('header')` → `False`
- [correto] `a=AnaliseCabecalhosHTTP(); a.adicionar('header', 'valor'); a.existe('header')` → `True`
- [errado] `a=AnaliseCabecalhosHTTP(); a.adicionar('A', 'V1'); a.adicionar('B', 'V2'); a.limpar(); len(a.dados)` → `0`
### 17: e0195 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `f= FilaPrioridade(); f.adicionar('b', 2); f.adicionar(10, 1); f.remover()` → `'b'`
- [correto] `f=FilaPrioridade(); f.adicionar('x', 'dois')` → `TypeError`
- [errado] `f= FilaPrioridade(); f.adicionar(5, 1); f.adicionar(1, 1); f.remover()` → `1`
- [correto] `f= FilaPrioridade(); f.remover()` → `IndexError`
- [errado] `f= FilaPrioridade(); f.adicionar(3, 2); f.consultar()` → `None`
- [correto] `f= FilaPrioridade(); f.adicionar(7, 1); f.adicionar(3, 1); f.adicionar(9, 1); f.remover()` → `7`
### 18: e0200 | formato ok | plano válido | notas: 1 corretos, 5 errados, 0 inavaliáveis
- [errado] `extrair_campos('nome={{ nome }}; idade={{ idade }}')` → `['nome', 'idade']`
- [errado] `extrair_campos('{{ campo }}')` → `ValueError`
- [errado] `extrair_campos('   {{ campo }    }')` → `[]`
- [correto] `renderizar_template('ola {{ nome }}!', {'nome': 'Ana'})` → `'ola Ana!'`
- [errado] `renderizar_template('ola {{ nome }}! \n {{ idade }} anos', {'nome': 'Ana'})` → `'ola Ana! \n None anos'`
- [errado] `renderizar_template('{{ campo }}', {})` → `ValueError`
### 19: e0202 | formato ok | plano válido | notas: 6 corretos, 4 errados, 0 inavaliáveis
- [correto] `rotacionar_esquerda([1, 2, 3, 4], 2)` → `[3, 4, 1, 2]`
- [errado] `rotacionar_esquerda([1, 2, 3], 4)` → `[1, 2, 3]`
- [errado] `rotacionar_direita([1, 2, 3, 4], 2)` → `[2, 3, 4, 1]`
- [errado] `rotacionar_direita([1, 2, 3], 4)` → `[2, 3, 1]`
- [correto] `rotacionar_esquerda([1, 2, 3], -1)` → `ValueError`
- [correto] `rotacionar_direita([], -1)` → `ValueError`
- [correto] `rotacionar_esquerda([], 5)` → `[]`
- [correto] `rotacionar_direita((), 3)` → `[]`
- [errado] `lista=[1,2]; r=rotacionar_esquerda(lista, 3); (r, lista)` → `(['', ''], [1, 2])`
- [correto] `rotacionar_esquerda([1, 2, 3, 4], 2) == rotacionar_direita([1, 2, 3, 4], 2)` → `True`
### 20: e0207 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `calcular_prazo_entrega('2024-01-01', 5)` → `'2024-01-06'`
- [correto] `calcular_prazo_entrega('2024-01-08', 3)` → `'2024-01-11'`
- [errado] `calcular_prazo_entrega('2024-02-29', 5)` → `ValueError`
- [correto] `calcular_prazo_entrega('2024-01-01', -2)` → `ValueError`
- [correto] `calcular_prazo_entrega('2024-01-15', 0)` → `'2024-01-15'`
- [errado] `calcular_prazo_entrega('2024-01-01', 7)` → `'2024-01-08'`
### 21: e0235 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `vencimentos_por_mes([('Ana', 10), ('Beto', 25)], 5)` → `['Ana', 'Beto']`
- [correto] `vencimentos_por_mes([('Ana', 15)], 0)` → `ValueError`
- [correto] `vencimentos_por_mes([('Ana', 32)], 5)` → `ValueError`
- [correto] `vencimentos_por_mes([('Zeca', 15), ('Ana', 10), ('Beto', 25)], 5)` → `['Ana', 'Beto', 'Zeca']`
- [correto] `vencimentos_por_mes([('Ana', 30)], 7)` → `['Ana']`
- [correto] `vencimentos_por_mes([('Ana', 1)], 8)` → `['Ana']`
### 22: e0238 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [errado] `c=ContadorPares(); c.adicionar(2); c.adicionar(2); c.obter_contagem()` → `2`
- [correto] `c=ContadorPares(); c.adicionar(None)` → `ValueError`
- [errado] `c=ContadorPares(); c.adicionar(5); c.adicionar(5); c.adicionar(6); c.obter_contagem()` → `2`
- [correto] `c=ContadorPares(); c.adicionar(1); c.resetar(); c.obter_contagem()` → `0`
- [correto] `c=ContadorPares(); c.adicionar(7); c.obter_contagem()` → `0`
- [correto] `c=ContadorPares(); c.adicionar(3); c.adicionar(3); c.adicionar(4); c.obter_contagem()` → `1`
### 23: e0273 | formato ok | plano válido | notas: 3 corretos, 5 errados, 0 inavaliáveis
- [correto] `validar_arquivo({'nome': 'imagem.png', 'tamanho': 1000000, 'tipo': 'image/png'})` → `True`
- [correto] `validar_arquivo({'nome': 'documento.pdf', 'tamanho': 5000000, 'tipo': 'application/pdf'})` → `True`
- [correto] `validar_arquivo({'nome': 'foto.jpg', 'tamanho': 10000000, 'tipo': 'image/jpg'})` → `False`
- [errado] `validar_arquivo({'nome': 'texto.txt', 'tamanho': 1000000, 'tipo': 'text/plain'})` → `False`
- [errado] `validar_arquivo({'nome': 'arquivo.zip', 'tamanho': 1000000, 'tipo': 'application/zip'})` → `ValueError`
- [errado] `validar_arquivo({'nome': 'arquivo', 'tamanho': 1000000, 'tipo': 'image/png'})` → `ValueError`
- [errado] `filtrar_validos([{'nome': 'foto1.png', 'tamanho': 1000000, 'tipo': 'image/png'}, {'nome': 'foto2.jpeg', 'taman` → `[{'nome': 'foto1.png', 'tamanho': 1000000, 'tipo': 'image/png'}, {'nom`
- [errado] `filtrar_validos([{'nome': 'foto1.png', 'tamanho': 1000000, 'tipo': 'image/png'}, {'nome': 'invalido', 'tamanho` → `[{'nome': 'foto1.png', 'tamanho': 1000000, 'tipo': 'image/png'}]`
### 24: e0282 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
{"casos": [{"criterio": "A classe deve inicializar com ambos os times zerados.", "entrada": "placar = PlacarBasquete(); (placar.consultar_placar(), placar.reiniciar())", "esperado": ("{'A': 0, 'B': 0}", "None")}, {"criterio": "O método registrar_cesta deve aceitar apenas time 'A' ou 'B' e pontos 1, 2 ou 3, somando ao respectivo time.", "entrada": "placar = PlacarBasquete(); placar.registrar_cesta('A', 3); placar.consultar_placar()", "esperado": "{'A': 3, 'B': 0}"}, {"criterio": "O método registr
```
### 25: e0284 | formato ok | plano válido | notas: 1 corretos, 7 errados, 0 inavaliáveis
- [errado] `calcular_nivel_experiencia(0)` → `(1, 0)`
- [errado] `calcular_nivel_experiencia(100)` → `(1, 100)`
- [errado] `calcular_nivel_experiencia(299)` → `(2, 100)`
- [errado] `calcular_nivel_experiencia(599)` → `(3, 100)`
- [errado] `calcular_nivel_experiencia(300)` → `(2, 0)`
- [errado] `calcular_nivel_experiencia(599)` → `(3, 0)`
- [correto] `calcular_nivel_experiencia(-1)` → `ValueError`
- [errado] `calcular_nivel_experiencia(1000)` → `(5, 100)`
### 26: e0295 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `vencedor_dados(5, 3)` → `'Jogador 1 venceu'`
- [correto] `vencedor_dados(2, 6)` → `'Jogador 2 venceu'`
- [correto] `vencedor_dados(4, 4)` → `'Empate'`
- [correto] `vencedor_dados(1.5, 3)` → `ValueError`
- [correto] `vencedor_dados(0, 6)` → `ValueError`
- [correto] `vencedor_dados(5, 7)` → `ValueError`
### 27: e0299 | formato ok | plano válido | notas: 3 corretos, 6 errados, 0 inavaliáveis
- [errado] `serializar_registros([{'nome': 'Ana', 'idade': 30}, {'cidade': 'Sao Paulo'}])` → `'nome=Ana,idade=30 cidade=S\'ao Paulo'`
- [errado] `serializar_registros([{'texto': 'oi \"ola\"'}])` → `'texto=\x22oi \\\x27ola\x22'`
- [errado] `serializar_registros([{'numero': 123}, {'preco': 9.8}])` → `'numero=123 preco=9.8'`
- [errado] `serializar_registros([{'ativo': True}, {'vivo': False}])` → `'ativo=true vivo=false'`
- [errado] `serializar_registros([{'valor': None}])` → `'valor=NULL'`
- [correto] `serializar_registros('não é lista')` → `TypeError`
- [correto] `serializar_registros([{'a': 1}, 'invalido'])` → `TypeError`
- [errado] `serializar_registros([{'idade': 30}])` → `TypeError`
- [correto] `serializar_registros([{'valores': [1,2]}])` → `ValueError`
### 28: e0301 | formato ok | plano válido | notas: 5 corretos, 0 errados, 0 inavaliáveis
- [correto] `r={}; adicionar_registro(r, 'a', 10); r` → `{'a': 10}`
- [correto] `r={'a': 1}; adicionar_registro(r, 'a', 20)` → `ValueError`
- [correto] `r={'x': 1, 'y': 2}; remover_registro(r, 'x'); r` → `{'y': 2}`
- [correto] `r={'a': 1}; remover_registro(r, 'b')` → `KeyError`
- [correto] `r={}; adicionar_registro(r, 'k', 1); remover_registro(r, 'k'); r` → `{}`
### 29: e0304 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `mesclar_ambientes([{'DB_HOST': 'localhost', 'DB_PORT': 5432}, {'DB_HOST': 'db.prod'}])` → `{'DB_HOST': 'db.prod', 'DB_PORT': 5432}`
- [correto] `mesclar_ambientes([{'API_KEY': 'abc123'}, {'API_KEY': 'def456'}])` → `{'API_KEY': 'def456'}`
- [correto] `mesclar_ambientes([{'DB': {'host': 'local', 'port': 5432}}, {'DB': {'host': 'prod'}}])` → `{'DB': {'host': 'prod', 'port': 5432}}`
- [correto] `mesclar_ambientes('não é lista')` → `TypeError`
- [correto] `mesclar_ambientes([{'DB_HOST': 'x'}, 'invalido'])` → `TypeError`
- [correto] `mesclar_ambientes([])` → `{}`
### 30: e0312 | formato ok | plano válido | notas: 3 corretos, 4 errados, 0 inavaliáveis
- [correto] `VersionamentoConfig({'a': 1}).obter(1)` → `{'a': 1}`
- [errado] `(lambda v: (v.atualizar({}), v.obter(v.versao+1)))(VersionamentoConfig({'x': 9})).versao` → `2`
- [correto] `VersionamentoConfig({'a': 1}).obter(0)` → `ValueError`
- [correto] `VersionamentoConfig({'a': 1}).obter(2)` → `ValueError`
- [errado] `VersionamentoConfig({'a': 1, 'b': 2}).diff(VersionamentoConfig({'a': 1}), VersionamentoConfig({'b': 2, 'c': 3}` → `{'adicionadas': ['b'], 'removidas': [], 'alteradas': [('b', 2)], 'inal`
- [errado] `vc=VersionamentoConfig({'a': [1,2]}) ; vc.obter(vc.versao).update(b=3); vc.diff(vc.obter(vc.versao), Versionam` → `ValueError`
- [errado] `VersionamentoConfig().atualizar({'k': 1}).atualizar({'k': 2}).obter(1)` → `{'k': 2}`
### 31: e0323 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `ranking_empates([('Ana', 8), ('Beto', 7), ('Carlos', 9)])` → `[('3', 'Carlos', 9)', ('1', 'Ana', 8)', ('2', 'Beto', 7)]`
- [errado] `ranking_empates([('A', 5), ('B', 5), ('C', 5)])` → `[('1', 'A', 5)', ('2', 'B', 5)', ('3', 'C', 5)]`
- [correto] `ranking_empates([])` → `ValueError`
- [correto] `ranking_empates([('A', 10, 2)])` → `ValueError`
- [correto] `ranking_empates([('A', 'dois')])` → `ValueError`
- [errado] `ranking_empates([('X', 6), ('Y', 6), ('Z', 6)])` → `[('1', 'X', 6)', ('2', 'Y', 6)', ('3', 'Z', 6)]`
### 32: e0383 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `editor=Editor(); editor.fazer('x'); editor.desfazer()` → `['x']`
- [errado] `editor=Editor(); editor.fazer('y'); editor.fazer('z'); editor.fazer('w')` → `['w', 'z', 'y']`
- [correto] `editor=Editor(); editor.fazer('a'); editor.fazer('b'); editor.desfazer(); editor.desfazer()` → `[]`
- [errado] `editor=Editor(); editor.fazer('p'); editor.desfazer()` → `[('p')]`
- [correto] `Editor().desfazer()` → `ValueError`
- [errado] `editor=Editor(); editor.fazer('s'); editor.fazer('t'); editor.desfazer(); editor.fazer('u'); editor.desfazer()` → `['u']`
### 33: e0392 | formato ok | plano válido | notas: 2 corretos, 3 errados, 0 inavaliáveis
- [correto] `desvio_padrao([])` → `ValueError`
- [correto] `desvio_padrao([1, 'a', 3])` → `TypeError`
- [errado] `desvio_padrao([10, 12, 23, 23, 16, 29, 26])` → `4.872983346207417`
- [errado] `desvio_padrao((x**2 for x in [1, 2, 3]))` → `2.0`
- [errado] `desvio_padrao([100, -50, 25])` → `41.18033988749895`
### 34: e0393 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `graus_para_rad(180)` → `3.141592653589793`
- [correto] `rad_para_graus(3.141592653589793)` → `180.0`
- [correto] `(lambda f: (f(90), f(-45.0)))(graus_para_rad)` → `(1.5707963267948966, -0.7853981633974483)`
- [correto] `graus_para_rad('90')` → `TypeError`
- [correto] `graus_para_rad(180)` → `3.141592653589793`
- [correto] `rad_para_graus(math.pi)` → `180.0`
### 35: e0420 | formato ok | plano válido | notas: 7 corretos, 0 errados, 0 inavaliáveis
- [correto] `divisores_primos(0)` → `ValueError`
- [correto] `divisores_primos(-5)` → `ValueError`
- [correto] `divisores_primos(2)` → `[2]`
- [correto] `divisores_primos(7)` → `[7]`
- [correto] `divisores_primos(10)` → `[2, 5]`
- [correto] `divisores_primos(15)` → `[3, 5]`
- [correto] `divisores_primos(8)` → `[2]`
### 36: e0425 | formato ok | plano inválido | notas: 4 corretos, 2 errados, 1 inavaliáveis
- [correto] `pares_na_faixa(1.5, 5)` → `TypeError`
- [correto] `impares_na_faixa(1.5, 5)` → `TypeError`
- [correto] `pares_na_faixa(6, 3)` → `ValueError`
- [errado] `pares_na_faixa(0, 10)` → `[0, 2, 4, 6, 8]`
- [inavaliavel] `impar_na_faixa(0, 10)` → `[1, 3, 5, 7, 9]`
- [correto] `pares_na_faixa(4, 4)` → `[4]`
- [errado] `pares_na_faixa(-5, -1)` → `[]`
### 37: e0433 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [errado] `pontuacao_final(10, 3, 5)` → `25`
- [correto] `pontuacao_final(-1, 3, 5)` → `ValueError`
- [correto] `pontuacao_final(10, -2, 5)` → `ValueError`
- [correto] `pontuacao_final(10, 3, 0)` → `ValueError`
- [correto] `pontuacao_final(8, 2, 10)` → `60`
- [errado] `pontuacao_final(7, 4, 3)` → `-9`
### 38: e0434 | formato ok | plano válido | notas: 10 corretos, 1 errados, 0 inavaliáveis
- [correto] `para_moeda(0)` → `'R$ 0,00'`
- [correto] `para_moeda(10)` → `'R$ 10,00'`
- [correto] `para_moeda(-3.14)` → `ValueError`
- [correto] `para_moeda(1/3)` → `'R$ 0,33'`
- [correto] `para_moeda(1234)` → `'R$ 1.234,00'`
- [correto] `para_moeda(1234.5)` → `'R$ 1.234,50'`
- [correto] `para_moeda('-5')` → `ValueError`
- [correto] `extrair_valor('R$ 1.234,56')` → `1234.56`
- [errado] `extrair_valor(' R $ 1.234 , 56 ')` → `1234.56`
- [correto] `extrair_valor('R$ 987,00')` → `987.0`
- [correto] `extrair_valor('1234')` → `ValueError`
### 39: e0450 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [correto] `c=Conta(); c.saque(-1)` → `ValueError`
- [errado] `c=Conta(10); c.saque(20)` → `ValueError`
- [correto] `c=Conta(); c.deposito(100); c.saque(30); c.saldo()` → `70`
- [correto] `c=Conta(); c.deposito(50); c.saldo()` → `50`
- [errado] `c=Conta(70); c.deposito(30); c.saque(10); c.saldo()` → `70`
- [correto] `Conta().saldo()` → `0`
### 40: e0455 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `calcula_frete({'Sao Paulo': (50.0, 10.0), 'Rio': (60.0, 8.0)}, 'Sao Paulo', 2)` → `70.0`
- [correto] `calcula_frete({'Sao Paulo': (50.0, 10.0), 'Rio': (60.0, 8.0)}, 'Rio', 0)` → `60.0`
- [correto] `calcula_frete({}, 'Brasil', 1)` → `ValueError`
- [correto] `calcula_frete({'Sao Paulo': (50.0, 10.0), 'Rio': (60.0, 8.0)}, 'Rio', -3)` → `ValueError`
- [errado] `calcula_frete({'A': (9.99, 2.0)}, 'A', 5)` → `15.98`
- [correto] `calcula_frete({}, 'Z', 1)` → `ValueError`
### 41: e0456 | formato ok | plano válido | notas: 6 corretos, 1 errados, 0 inavaliáveis
- [correto] `LeitorLinhaCSV('a,b').ler()` → `['a', 'b']`
- [correto] `LeitorLinhaCSV(None)` → `ValueError`
- [correto] `LeitorLinhaCSV(123)` → `ValueError`
- [correto] `LeitorLinhaCSV('x,y,z').ler()` → `['x', 'y', 'z']`
- [correto] `LeitorLinhaCSV('a,,b').ler()` → `['a', '', 'b']`
- [errado] `LeitorLinhaCSV('  a , b   ').ler()` → `['a', 'b']`
- [correto] `LeitorLinhaCSV('abc').ler()` → `['abc']`
### 42: e0466 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [correto] `calcular_total([])` → `ValueError`
- [correto] `calcular_total([("maçã", -5, 2)])` → `ValueError`
- [correto] `calcular_total([("banana", 2.5, -3)])` → `ValueError`
- [errado] `calcular_total([("maçã", 2.0, 5), ("uva", 1.5, 4)])` → `17.0`
- [errado] `calcular_total([("pera", 50.0, 1)])` → `45.0`
- [correto] `calcular_total([("laranja", 10.0, 10)])` → `100.0`
### 43: e0472 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `VersaoConfiguracao(0)` → `ValueError`
- [correto] `VersaoConfiguracao({'a': 1}).aplicar_mudancas('nao_dict')` → `TypeError`
- [errado] `(lambda v: (v.aplicar_mudancas({}), v.obter_estado()))([VersaoConfiguracao({'a': 1})])` → `(({'a': 1}, ('1', {'a': 1})),)`
- [correto] `VersaoConfiguracao({'x': 1}, 2).aumentar_versao()` → `3`
- [errado] `VersaoConfiguracao({'y': 2}, 1).obter_estado()` → `('1', {'y': 2'})`
- [errado] `VersaoConfiguracao({'u': 3}, 9).aumentar_versao(); VersaoConfiguracao({'v': 4}, 8).obter_estado()` → `('8', {'v': 4'})`
### 44: e0520 | formato ok | plano válido | notas: 5 corretos, 2 errados, 0 inavaliáveis
- [correto] `contar_palavras_e_frases(123)` → `TypeError`
- [correto] `contar_palavras_e_frases(None)` → `TypeError`
- [correto] `contar_palavras_e_frases('   ')` → `ValueError`
- [errado] `contar_palavras_e_frases('Olá mundo Olá Python')` → `{'palavras': 2, 'frases': 0}`
- [errado] `contar_palavras_e_frases('Oi! Tudo bem? Eu sou novo aqui.')` → `{'palavras': 6, 'frases': 2}`
- [correto] `contar_palavras_e_frases('Um dois três')` → `{'palavras': 3, 'frases': 0}`
- [correto] `contar_palavras_e_frases('Abc def')` → `{'palavras': 2, 'frases': 0}`
### 45: e0534 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `ConfiguracaoCamadas().carregar_configuracao('nao_dict', {}, 'ambiente')` → `ValueError`
- [correto] `ConfiguracaoCamadas().carregar_configuracao({'a': 1}, {'b': 2}, {'c': 3})` → `{'a': 1, 'b': 2, 'c': 3}`
- [errado] `ConfiguracaoCamadas().carregar_configuracao({'db': {'host': 'localhost', 'port': 5432}}, {'db': {'host': 'prod` → `{'db': {'host': 'dev', 'port': 5432}}`
- [correto] `ConfiguracaoCamadas().carregar_configuracao({'app': {'debug': True}}, {}, {})` → `{'app': {'debug': True}}`
- [correto] `ConfiguracaoCamadas().carregar_configuracao({}, {'api_key': 'abc123'}, {})` → `{'api_key': 'abc123'}`
- [correto] `ConfiguracaoCamadas().carregar_configuracao({'timezone': 'America/Sao_Paulo'}, {}, {'TZ': 'UTC'})` → `{'timezone': 'America/Sao_Paulo', 'TZ': 'UTC'}`
### 46: e0540 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `c=Classificacao(); c.adicionar({'nome':'Ana','idade':30}); c.adicionar({'idade':30,'cidade':'Sao Paulo'}); c.a` → `[{'nome':'Ana','idade':30}, {'idade':30,'cidade':'Rio de Janeiro'}, {'`
- [errado] `c=Classificacao(); c.adicionar('um'); c.adicionar(1); c.ordenar([('valor','crescente')]); c.itens` → `[1, 'um']`
- [correto] `c=Classificacao(); c.adicionar({'x':1,'y':2}); c.adicionar({'x':2,'y':1}); c.ordenar([('x','crescente'),('y','` → `[{'x':1,'y':2}, {'x':2,'y':1}]`
- [correto] `c=Classificacao(); c.adicionar({'a':1}); c.ordenar([('a','invalida')])` → `ValueError`
- [correto] `c=Classificacao(); c.adicionar({'a':1}); c.adicionar({'b':2}); c.ordenar([('a','crescente'),('b','crescente')]` → `ValueError`
- [errado] `c=Classificacao(); c.adicionar({'n':[1,2]}); c.ordenar([('n','crescente')])` → `ValueError`
### 47: e0584 | formato ok | plano válido | notas: 8 corretos, 0 errados, 0 inavaliáveis
- [correto] `proximo_estado_pedido('novo', 'cancelado')` → `'cancelado'`
- [correto] `proximo_estado_pedido('novo', 'pago')` → `'pago'`
- [correto] `proximo_estado_pedido('pago', 'cancelado')` → `'cancelado'`
- [correto] `proximo_estado_pedido('enviado', 'entregue')` → `'entregue'`
- [correto] `proximo_estado_pedido('entregue', 'cancelado')` → `ValueError`
- [correto] `pode_avancar_estado_pedido('novo', 'pago')` → `True`
- [correto] `pode_avancar_estado_pedido('pago', 'cancelado')` → `True`
- [correto] `pode_avancar_estado_pedido('cancelado', 'entregue')` → `False`
### 48: e0587 | formato ok | plano válido | notas: 2 corretos, 5 errados, 0 inavaliáveis
- [errado] `normalizar_vendas([{"data": "2024-05-15", "vendedor": "Ana", "valor": 100}, {"data": "2024-06-01", "vendedor":` → `[{'data': '2024-05-15', 'vendedor': 'Ana', 'valor': 100, 'mes': '2024-`
- [errado] `vendas=[{"data":"2024-07-01","vendedor":"Carlos","valor":100},{"data":"2024-08-01","vendedor":"Carlos","valor"` → `[{'data': '2024-07-01', 'vendedor': 'Carlos', 'valor': 100, 'mes': '20`
- [errado] `vendas=[{"data":"2024-05-01","vendedor":"Ana","valor":100},{"data":"2024-05-01","vendedor":"Ana","valor":200},` → `{'2024-05': 300, '2024-06': 300}`
- [correto] `normalizar_vendas([{"data":"2024-05-15", "vendedor":"Ana"}])` → `ValueError`
- [errado] `normalizar_vendas([{"data":"2024-05-32", "vendedor":"Ana","valor":100}])` → `ValueError`
- [correto] `normalizar_vendas([{"data":"2024-05-15", "vendedor":"Ana","valor":-10}])` → `ValueError`
- [errado] `vendas=[{"data":"2024-13-01","vendedor":"Ana","valor":100}]` → `ValueError`
### 49: e0614 | formato ok | plano válido | notas: 10 corretos, 0 errados, 0 inavaliáveis
- [correto] `StatusHTTP(200).status_classe()` → `'Sucesso'`
- [correto] `StatusHTTP(201).status_classe()` → `'Sucesso'`
- [correto] `StatusHTTP(301).status_classe()` → `'Redirecionamento'`
- [correto] `StatusHTTP(302).status_classe()` → `'Redirecionamento'`
- [correto] `StatusHTTP(400).status_classe()` → `'Erro do Cliente'`
- [correto] `StatusHTTP(401).status_classe()` → `'Erro do Cliente'`
- [correto] `StatusHTTP(500).status_classe()` → `'Erro do Servidor'`
- [correto] `StatusHTTP(501).status_classe()` → `'Erro do Servidor'`
- [correto] `StatusHTTP(600).status_classe()` → `ValueError`
- [correto] `StatusHTTP(True).status_classe()` → `ValueError`
### 50: e0619 | formato ok | plano válido | notas: 4 corretos, 1 errados, 0 inavaliáveis
- [correto] `m=Matricula(); m.matricular('Ana', 8); m.obter_nota('Ana')` → `8`
- [correto] `m=Matricula(); m.matricular('Ana', 7); m.matricular('Ana', 9); m.obter_nota('Ana')` → `9`
- [correto] `m=Matricula(); m.matricular('Ana', -1)` → `ValueError`
- [correto] `m=Matricula(); m.obter_nota('Bruno')` → `None`
- [errado] `m=Matricula(); m.matricular('Carlos', 6); m.matricular('Ana', 8); m.listar_alunos()` → `['Ana', 'Carlos']`
### 51: e0633 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `Idade(2000, 2023).ano_nascimento` → `2000`
- [correto] `Idade(2000, 2023).ano_atual` → `2023`
- [correto] `Idade(1990, 2023).anos_completos()` → `33`
- [correto] `Idade(1990, 1990).anos_completos()` → `0`
- [correto] `Idade(1990, 1980)` → `ValueError`
- [errado] `(lambda i: (i.anos_completos(), i.anos_completos(2024)))(Idade(1990, 2023))` → `(33, 34)`
### 52: e0637 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `RaizPotencia().calcular(9, 2)` → `0`
- [errado] `(lambda r: (r.calcula(16, 2), r.calcular(16, 2)))(RaizPotencia())` → `(0, 0)`
- [errado] `RaizPotencia().calcular(10, 2)` → `5`
- [correto] `RaizPotencia().calcular(-4, 2)` → `ValueError`
- [correto] `RaizPotencia().calcular(16, -1)` → `ValueError`
- [correto] `RaizPotencia().calcular(9.5, 2)` → `ValueError`
### 53: e0639 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `extrair_diagonal_principal([])` → `ValueError`
- [correto] `extrair_diagonal_principal([[1, 2], [3]])` → `ValueError`
- [correto] `extrair_diagonal_principal([[1, 2, 3], [4, 5, 6], [7, 8, 9]])` → `[1, 5, 9]`
- [correto] `extrair_diagonal_secundaria([[1, 2, 3], [4, 5, 6], [7, 8, 9]])` → `[3, 5, 7]`
- [correto] `len(extrair_diagonal_principal([[1, 2], [3, 4]]))` → `2`
- [correto] `len(extrair_diagonal_secundaria([[1, 2], [3, 4]]))` → `2`
### 54: e0657 | formato ok | plano inválido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `aplicar_evento({'saldo': 10}, {'tipo': 'depositar', 'valor': 5})` → `{'saldo': 15}`
- [correto] `aplicar_evento({'saldo': 20}, {'tipo': 'sacar', 'valor': 7})` → `{'saldo': 13}`
- [correto] `aplicar_evento({'saldo': 5}, {'tipo': 'sacar', 'valor': 10})` → `ValueError`
- [correto] `aplicar_evento({'saldo': 10}, {'tipo': 'invalido', 'valor': 5})` → `ValueError`
- [correto] `reconstruir_estado([])` → `{"saldo": 0}`
- [correto] `reconstruir_estado([{'tipo': 'depositar', 'valor': 3}, {'tipo': 'sacar', 'valor': 2}])` → `{'saldo': 1}`
### 55: e0662 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
{"casos": [{"criterio": "O método para_romano converte inteiros de 1 a 3999 para numerais romanos, armazena o inteiro em ultimo_valor e retorna a string correspondente", "entrada": "ConversorNumeralRomano().para_romano(1)", "esperado": "'I'"}, {"criterio": "O método para_romano converte inteiros de 1 a 3999 para numerais romanos, armazena o inteiro em ultimo_valor e retorna a string correspondente", "entrada": "ConversorNumeralRomano().para_romano(10)", "esperado": "'X'"}, {"criterio": "O método
```
### 56: e0687 | formato ok | plano inválido | notas: 10 corretos, 0 errados, 0 inavaliáveis
- [correto] `extenso(0)` → `'zero'`
- [correto] `extenso(7)` → `'sete'`
- [correto] `extenso(30)` → `'trinta'`
- [correto] `extenso(60)` → `'sessenta'`
- [correto] `extenso(27)` → `'vinte e sete'`
- [correto] `extenso(84)` → `'oitenta e quatro'`
- [correto] `extenso(True)` → `ValueError`
- [correto] `extenso('25')` → `ValueError`
- [correto] `extenso(-1)` → `ValueError`
- [correto] `extenso(100)` → `ValueError`
### 57: e0693 | formato ok | plano válido | notas: 1 corretos, 5 errados, 0 inavaliáveis
- [correto] `LimpadorTexto(123)` → `TypeError`
- [errado] `LimpadorTexto('  olá   mundo  ').limpar()` → `'olá mundo'`
- [errado] `LimpadorTexto('linha1   extra').limpar()` → `'linha1 extra'`
- [errado] `LimpadorTexto('uma\n\nb duas\nc').limpar()` → `'uma\nb duas'`
- [errado] `LimpadorTexto('a\nb\na\nc').limpar()` → `'a\nb\nc'`
- [errado] `LimpadorTexto('x\ny\nx\nz').limpar()` → `'x\ny\nz'`
### 58: e0702 | formato ok | plano válido | notas: 6 corretos, 2 errados, 0 inavaliáveis
- [correto] `eh_armstrong(True)` → `ValueError`
- [correto] `eh_armstrong(153)` → `True`
- [correto] `eh_armstrong(100)` → `False`
- [errado] `proximo_armstrong(153)` → `153`
- [correto] `eh_armstrong(0)` → `True`
- [correto] `eh_armstrong(9)` → `True`
- [errado] `proximo_armstrong(1)` → `153`
- [correto] `proximo_armstrong(-1)` → `ValueError`
### 59: e0707 | formato ok | plano válido | notas: 7 corretos, 1 errados, 0 inavaliáveis
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('X-Request-Id', 'abc-def'); cabecalho.obter('x-request-id')` → `'abc-def'`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('Content-Type', 'application/json   '); cabecalho.obter('cont` → `'application/json'`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('Requisicao', 'GET'); cabecalho.obter('requisicao')` → `'GET'`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.obter('não-existe')` → `None`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.contem('status-code')` → `False`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('', 'valor')` → `ValueError`
- [correto] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('header', '')` → `ValueError`
- [errado] `cabecalho = CabecalhoHTTP(); cabecalho.adicionar('Nome', 'um'); cabecalho.adicionar('Valor', 'dois'); cabecalh` → `['Nome', 'Valor']`
### 60: e0708 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [correto] `calcular_pagamento(-100, 8)` → `ValueError`
- [correto] `calcular_pagamento(500, -5)` → `ValueError`
- [errado] `calcular_pagamento(1000, 4)` → `50.0`
- [errado] `calcular_pagamento(1000, 6)` → `700.0`
- [errado] `calcular_pagamento(1000, 15)` → `1900.0`
- [errado] `calcular_pagamento(800, 10)` → `1000.0`
### 61: e0714 | formato ok | plano inválido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `ord = OrdenadorMultiChave(); ord.adicionar('b', ['x']); ord.adicionar('a', ['x']); ord.classificar()` → `['a', 'b']`
- [errado] `ord = OrdenadorMultiChave(); ord.adicionar(10, [2]); ord.adicionar(9, [2]); ord.adicionar(8, [2]); ord.classif` → `[8, 9, 10]`
- [correto] `ord = OrdenadorMultiChave(); ord.adicionar('um', [])` → `ValueError`
- [correto] `ord = OrdenadorMultiChave(); ord.classificar()` → `ValueError`
- [errado] `ord = OrdenadorMultiChave(); ord.adicionar('primeiro', ['desc']); ord.classificar(); ord.classificar()` → `ValueError`
- [errado] `ord = OrdenadorMultiChave(); ord.adicionar(1, ['int', 'str']); ord.classificar()` → `ValueError`
### 62: e0734 | formato ok | plano válido | notas: 2 corretos, 5 errados, 0 inavaliáveis
- [errado] `validar_dependencias({'soma': ['subtracao'], 'subtracao': [], 'mult': []})` → `ValueError`
- [correto] `validar_dependencias({'soma': ['invalido']})` → `ValueError`
- [correto] `validar_dependencias({'a': ['b'], 'b': ['a']})` → `ValueError`
- [errado] `ordenar_servicos({'soma': ['subtracao'], 'subtracao': [], 'mult': []})` → `['soma', 'subtracao', 'mult']`
- [errado] `ordenar_servicos({'x': ['y'], 'y': ['z'], 'z': []})` → `['x', 'y', 'z']`
- [errado] `ordenar_servicos({'a': ['b'], 'b': ['c'], 'c': []})` → `['a', 'b', 'c']`
- [errado] `ordenar_servicos({'nao_depende': [], 'depende': ['nao_depende']})` → `['depende', 'nao_depende']`
### 63: e0737 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [errado] `ConfigCamadas({}, 'teste', {}).obter('x')` → `ValueError`
- [correto] `ConfigCamadas({'a': 1}, {}, {}).obter('a')` → `1`
- [errado] `ConfigCamadas({'a': 1}, {'b': 2}, {}).obter('b')` → `None`
- [correto] `ConfigCamadas({'a': 1}, {'b': 2}, {'c': 3}).obter('c')` → `3`
- [correto] `ConfigCamadas({'a': 1}, {}, {}).obter('y')` → `None`
- [correto] `ConfigCamadas({'a': 1}, {'b': 2}, {'c': 3}).obter('a')` → `1`
### 64: e0749 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `h=HistogramaMetricas(); h.adicionar('texto')` → `TypeError`
- [correto] `h=HistogramaMetricas(); h.adicionar(1.5)` → `None`
- [correto] `h=HistogramaMetricas(); r=h.adicionar(7); r` → `None`
- [correto] `h=HistogramaMetricas(); h.adicionar(3); h.adicionar(3); h.adicionar(3); h.distribuicao()` → `{3: 3}`
- [correto] `h=HistogramaMetricas(); h.adicionar(10); h.adicionar(20); h.adicionar(10); h.adicionar(20); h.distribuicao()` → `{10: 2, 20: 2}`
- [correto] `h=HistogramaMetricas(); h.distribuicao()` → `ValueError`
### 65: e0759 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `p=Particao(); p.adicionar(5); p.adicionar(1); p.adicionar(9); p.itens` → `[5, 1, 9]`
- [correto] `p=Particao(); p.particionar('nao eh funcao')` → `ValueError`
- [errado] `p=Particao(); p.adicionar(10); p.adicionar(-1); p.adicionar(7); p.particionar(lambda x: x>0)` → `[10, 7]`
- [errado] `p=Particao(); p.adicionar(10); p.adicionar(-1); p.adicionar(7); p.particionar(lambda x: x<0)` → `[-1]`
- [correto] `p=Particao(); p.adicionar(1); p.adicionar(2); p.particionar(lambda x: x%2==0); p.rejeitados()` → `[1]`
- [errado] `p=Particao(); p.adicionar(1); p.adicionar(2); p.particionar(lambda x: x>5); p.particionar(lambda x: x<10)` → `[6, 8]`
### 66: e0771 | formato ok | plano válido | notas: 6 corretos, 2 errados, 0 inavaliáveis
- [correto] `normalizar_cpf('12345678901')` → `'12345678901'`
- [correto] `normalizar_cpf('123456789')` → `ValueError`
- [correto] `normalizar_cpf('abcdefghij')` → `ValueError`
- [correto] `normalizar_cpf('11111111111')` → `ValueError`
- [errado] `normalizar_cpf('00000000000')` → `'00000000000'`
- [errado] `validar_cpf('11223344556')` → `True`
- [correto] `validar_cpf('11223344557')` → `False`
- [correto] `validar_cpf('abcde1234567')` → `ValueError`
### 67: e0781 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `calcular_pontos(5, 3)` → `3`
- [correto] `calcular_pontos(7, 7)` → `1`
- [correto] `calcular_pontos(3, 5)` → `0`
- [correto] `calcular_pontos(-1, 5)` → `ValueError`
- [correto] `saldo_gols(8, 4)` → `4`
- [errado] `saldo_gols(6, -2)` → `-8`
### 68: e0791 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `disparar_tiros([(0, 0), (0, 0)], {(0, 0)})` → `({(0, 0)}, {})`
- [errado] `disparar_tiros([(0, 0), (1, 1)], {(0, 0), (1, 1)})` → `({(0, 0), (1, 1)}, {})`
- [correto] `disparar_tiros([(0, 0, 0), (1, 1)], {(0, 0)})` → `ValueError`
- [correto] `verificar_estado_tiros({(0, 0), (1, 1)}, {(0, 0), (1, 1), (2, 2)})` → `True`
- [errado] `verificar_estado_tiros({(0, 0), (1, 1)}, {(0, 0), (1, 1), (2, 2), (3, 3)})` → `False`
- [errado] `verificar_estado_tiros([(0, 0)], {(0, 0)})` → `ValueError`
### 69: e0815 | formato ok | plano válido | notas: 6 corretos, 0 errados, 0 inavaliáveis
- [correto] `ComissaoVendas().calcular(100)` → `5.0`
- [correto] `ComissaoVendas().calcular(900)` → `45.0`
- [correto] `ComissaoVendas().calcular(1500)` → `150.0`
- [correto] `ComissaoVendas().calcular(7000)` → `1050.0`
- [correto] `ComissaoVendas().calcular(-10)` → `ValueError`
- [correto] `ComissaoVendas().calcular(0)` → `0.0`
### 70: e0816 | formato ok | plano inválido | notas: 1 corretos, 5 errados, 0 inavaliáveis
- [errado] `matricula_aluno('abc', [7,8])` → `ValueError`
- [errado] `matricula_aluno(123, [6,11])` → `ValueError`
- [errado] `ranking_turma({'A': [8,7], 'B': [6,9]})` → `[('A', {'nome': 'X', 'notas': [8, 7]}), ('B', {'nome': 'Y', 'notas': [`
- [errado] `ranking_turma({'Z': [7,8], 'A': [7,8]})` → `[('A', {'nome': 'X', 'notas': [7, 8]}), ('Z', {'nome': 'Y', 'notas': [`
- [correto] `ranking_turma({})` → `[]`
- [errado] `ranking_turma({'P': []})` → `[('', {})]`
### 71: q0031 | formato ok | plano válido | notas: 5 corretos, 1 errados, 0 inavaliáveis
- [correto] `comuns_tres([3, 1, 2], [2, 5, 1], [1, 9])` → `[1]`
- [correto] `comuns_tres([10, 10, 10], [7, 10, 14], [10, 18])` → `[10]`
- [correto] `comuns_tres([1, 2], [3, 4], [5, 6])` → `[]`
- [correto] `comuns_tres((1, 2), [3, 4], [5, 6])` → `TypeError`
- [correto] `comuns_tres([], [], [])` → `[]`
- [errado] `comuns_tres([-5, -2, 0], [0, 5, 10], [0, 5])` → `[0, 5]`
### 72: q0069 | formato ok | plano válido | notas: 4 corretos, 5 errados, 0 inavaliáveis
- [errado] `contar_ilhas([[0, 0, 0], [1, 1, 0], [0, 0, 0]])` → `2`
- [errado] `contar_ilhas([[1, 1], [1, 0]])` → `2`
- [errado] `contar_ilhas([[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])` → `3`
- [correto] `contar_ilhas([])` → `0`
- [errado] `maior_ilha([[0, 0, 0], [0, 1, 0], [0, 0, 0]])` → `3`
- [errado] `maior_ilha([[1, 1, 1], [1, 0, 0], [1, 0, 0]])` → `9`
- [correto] `maior_ilha([[]])` → `0`
- [correto] `maior_ilha([[0]])` → `0`
- [correto] `maior_ilha([[1, 1], [1]])` → `ValueError`
### 73: q0051 | formato ok | plano válido | notas: 7 corretos, 2 errados, 0 inavaliáveis
- [correto] `valor_noite("simples")` → `120.0`
- [correto] `valor_noite("duplo")` → `180.0`
- [correto] `valor_noite("suite")` → `300.0`
- [correto] `valor_noite("luxo")` → `450.0`
- [correto] `valor_noite("quarto_extra")` → `ValueError`
- [errado] `total_hospedagem("duplo", 3)` → `570.0`
- [errado] `total_hospedagem("duplo", 3, cafe=True)` → `607.5`
- [correto] `total_hospedagem("duplo", 0)` → `ValueError`
- [correto] `total_hospedagem("invalido", 3)` → `ValueError`
### 74: q0077 | formato ok | plano válido | notas: 4 corretos, 3 errados, 0 inavaliáveis
- [correto] `RolagemDados().total()` → `0`
- [correto] `(lambda r: (r.processar('34'), r.total()))(RolagemDados())` → `(7, 7)`
- [errado] `(lambda r: (r.processar('dd1'), r.total()))(RolagemDados())` → `(3, 3)`
- [correto] `r=RolagemDados(); r.processar('5'); r.total()` → `5`
- [errado] `(lambda r: (r.processar('2d'), r.processar('3'), r.total()))(RolagemDados())` → `(5, 8, 8)`
- [correto] `r=RolagemDados(); r.processar('ab')` → `ValueError`
- [errado] `(lambda r: (r.processar('x'), r.total()))(RolagemDados())` → `(0, 0)`
### 75: q0063 | formato ok | plano válido | notas: 3 corretos, 3 errados, 0 inavaliáveis
- [errado] `contar_por_faixa([0, 5, 10, 15], 5)` → `[(0, 5, 2), (5, 10, 2), (10, 15, 1)]`
- [errado] `contar_por_faixa([0, 10, 20, 30], 5)` → `[(0, 5, 4), (5, 10, 2), (10, 15, 1), (15, 20, 1), (20, 30, 1)]`
- [errado] `contar_por_faixa([3, 7, 9, 12], 3)` → `[(0, 3, 3), (3, 6, 1), (6, 9, 1), (9, 12, 1)]`
- [correto] `contar_por_faixa([], 3)` → `[]`
- [correto] `contar_por_faixa([0, 5], 0)` → `ValueError`
- [correto] `contar_por_faixa([-1, 5], 3)` → `ValueError`
### 76: q0055 | formato ok | plano válido | notas: 2 corretos, 4 errados, 0 inavaliáveis
- [errado] `MisturadorListas([1, 2, 3], ['a', 'b']).intercalar()` → `[1, 'a', 2, 'b', 3]`
- [errado] `MisturadorListas([], [True, False]).intercalar()` → `[False, True]`
- [correto] `MisturadorListas([1, 2], [3]).intercalar()` → `ValueError`
- [errado] `m=MisturadorListas([1]); m.intercalar(); m.intercalado` → `[1]`
- [errado] `MisturadorListas([10, -3], [5, 7]).total()` → `18`
- [correto] `m=MisturadorListas([1, 2], [3, 4]); m.intercalar(); m.a` → `[1, 2]`
### 77: q0038 | formato ok | plano válido | notas: 6 corretos, 1 errados, 0 inavaliáveis
- [correto] `t=ArvoreBinariaBusca(); t.inserir(5); t.inserir(1); t.inserir(9); t.em_ordem()` → `[1, 5, 9]`
- [errado] `t=ArvoreBinariaBusca(); t.inserir(7); t.inserir(7); t.inserir(3); t.em_ordem()` → `[3, 7, 7]`
- [correto] `t=ArvoreBinariaBusca(); t.inserir(4); t.buscar(4)` → `True`
- [correto] `t=ArvoreBinariaBusca(); t.inserir(6); t.buscar(8)` → `False`
- [correto] `t=ArvoreBinariaBusca(); t.inserir('x')` → `TypeError`
- [correto] `t=ArvoreBinariaBusca(); t.inserir(-1)` → `ValueError`
- [correto] `ArvoreBinariaBusca().em_ordem()` → `[]`
### 78: q0064 | formato ok | plano válido | notas: 2 corretos, 3 errados, 1 inavaliáveis
- [correto] `em_ordem(None)` → `[]`
- [errado] `inserir(None, 5)` → `5`
- [errado] `inserir(inserir(None, 2), 7); em_ordem(None)` → `[2, 5, 7]`
- [errado] `n=inserir(None, 3); n=inserir(n, 3); em_ordem(None)` → `[3]`
- [correto] `inserir(None, 9).valor` → `9`
- [inavaliavel] `inserir(inserir(None, 1), 6); in=inserir(inserir(None, 4), 8); em_ordem(None)` → `[1, 4, 6, 8]`
### 79: q0017 | formato ok | plano válido | notas: 4 corretos, 2 errados, 0 inavaliáveis
- [correto] `d=DiffLinhas(['a','b']); d.acrescentadas(['c','d','b'])` → `['c', 'd']`
- [errado] `d=DiffLinhas(['a','b']); d.removidas(['c','d','b'])` → `['c', 'd']`
- [correto] `d=DiffLinhas(['a','b']); d.mantidas(['a','b','c'])` → `['a', 'b']`
- [correto] `d=DiffLinhas(['a']); d.acrescentadas([1])` → `ValueError`
- [errado] `DiffLinhas(['a','b'])` → `ValueError`
- [correto] `d=DiffLinhas(['x','y']); d.acrescentadas(['z']); d.removidas(['w','z']); sorted(d.mantidas(['x','y']))` → `['x', 'y']`

## sintetico_base

### 0: e0024 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "rot13 recebe uma string",
        "entrada": "Hello World!",
        "esperado": "Uryyb Jbeyq!"
    },
    {
        "criterio": "rot13 mantém letras maiúsculas",
        "entrada": "HELLO WORLD!",
        "esperado": "URYYB JBYEQ!"
    },
    {
        "criterio": "rot13 mantém letras minúsculas",
        "entrada": "hello world!",
        "esperado": "uryyb jbyeq!"
    },
    {
        "criterio": "rot13 preserva caracteres não-alfabéticos",
        "entrad
```
### 1: e0029 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "calcular_pontuacao_base",
        "entrada": {"tempo_segundos": 10, "erros": 5},
        "esperado": 900
    },
    {
        "criterio": "calcular_pontuacao_base",
        "entrada": {"tempo_segundos": -1, "erros": 5},
        "erro": "ValueError"
    },
    {
        "criterio": "calcular_pontuacao_base",
        "entrada": {"tempo_segundos": 0, "erros": 0},
        "esperado": 1000
    }
]
```

```json
[
    {
        "criterio": "calcular_pontuacao_final"
```
### 2: e0031 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Retorna 'equilátero' quando os três lados são iguais e formam um triângulo válido",
        "entrada": {"a": 5, "b": 5, "c": 5},
        "esperado": "equilátero"
    },
    {
        "criterio": "Retorna 'isósceles' quando exatamente dois lados são iguais e formam um triângulo válido",
        "entrada": {"a": 5, "b": 5, "c": 6},
        "esperado": "isósceles"
    },
    {
        "criterio": "Retorna 'escaleno' quando os três lados são diferentes e formam u
```
### 3: e0062 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "calcular_pontos_nivel",
        "entrada": {"pontuacao_base": 100, "dificuldade": 3, "completou": true},
        "esperado": 3500
    },
    {
        "criterio": "calcular_pontos_nivel",
        "entrada": {"pontuacao_base": -100, "dificuldade": 3, "completou": false},
        "esperado": "ValueError"
    },
    {
        "criterio": "calcular_pontos_nivel",
        "entrada": {"pontuacao_base": 100, "dificuldade": 5, "completou": false},
        "esperado":
```
### 4: e0069 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Levanta ValueError se a entrada não for um dicionário ou faltar qualquer campo obrigatório",
        "entrada": {"nome": "", "email": "invalid.email@domain.com", "idade": 90, "cpf": "12345678901"},
        "esperado": {
            "valido": False,
            "erros": [
                "Nome não pode ser vazio"
            ]
        }
    },
    {
        "criterio": "Adiciona erro \"Nome não pode ser vazio\" se nome não for string ou for vazio após strip",

```
### 5: e0084 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor aceita um dicionário opcional de produtos iniciais e levanta ValueError se alguma quantidade inicial não for inteiro não negativo.",
        "entrada": {"produtos_iniciais": {}},
        "esperado": "ValueError"
    },
    {
        "criterio": "adicionar(nome, quantidade) incrementa o estoque do produto; levanta ValueError se quantidade não for inteiro positivo.",
        "entrada": {"estoque": {"produto_a": 1}, "adicionar": {"produto_b", 2}},
 
```
### 6: e0086 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A classe CalculadoraJuros deve ser instanciada com uma taxa de juros anual.",
        "entrada": "taxa = 0.05",
        "esperado": "Taxa de juros anual válida."
    },
    {
        "criterio": "O método calcular_juros_simples deve retornar o valor correto quando capital e tempo são não-negativos.",
        "entrada": "capital = 1000, tempo_anos = 1",
        "esperado": "Valor corrigido de juros simples."
    },
    {
        "criterio": "O método calcular_
```
### 7: e0087 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Retorna dicionário onde cada chave é um elemento do iterável e o valor é a quantidade de ocorrências",
        "entrada": [1, 2, 2, 3],
        "esperado": {1: 1, 2: 2, 3: 1}
    },
    {
        "criterio": "Se ordenar=True, as chaves do dicionário retornado estão em ordem crescente",
        "entrada": [1, 2, 2, 3],
        "ordenar": true,
        "esperado": {1: 1, 2: 2, 3: 1}
    },
    {
        "criterio": "Se ordenar=False, a ordem das chaves segue a 
```
### 8: e0109 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Retorna o preco_inteiro quando tipo_ingresso eh \"inteira\"",
        "entrada": {"preco_inteiro": 100.0, "tipo_ingresso": "inteira"},
        "esperado": 100.0
    },
    {
        "criterio": "Retorna metade do preco_inteiro quando tipo_ingresso eh \"meia\" e eh_estudante eh True",
        "entrada": {"preco_inteiro": 200.0, "tipo_ingresso": "meia", "eh_estudante": true},
        "esperado": 100.0
    },
    {
        "criterio": "Retorna preco_inteiro quan
```
### 9: e0114 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função extrair_iniciais('João Pedro Silva') deve retornar 'J.P.S.'",
        "entrada": "João Pedro Silva",
        "esperado": "J.P.S."
    },
    {
        "criterio": "A função extrair_iniciais('Maria da Silva') deve retornar 'M.S.'",
        "entrada": "Maria da Silva",
        "esperado": "M.S."
    },
    {
        "criterio": "A função extrair_iniciais('José dos Santos') deve retornar 'J.S.S.'",
        "entrada": "José dos Santos",
        "esperado
```
### 10: e0124 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "agrupar_vendas_por_mes deve retornar dicionário mapeando 'YYYY-MM' para lista de valores do mês",
        "entrada": [
            ["2023-01-15", 100],
            ["2023-02-28", 150],
            ["2023-03-31", 200]
        ],
        "esperado": {
            "2023-01": [100],
            "2023-02": [150],
            "2023-03": [200]
        }
    },
    {
        "critério": "total_por_mes deve retornar dicionário mapeando 'YYYY-MM' para soma dos valores 
```
### 11: e0125 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Retorna um novo dicionário contendo todas as chaves de ambos os dicionários",
        "entrada": {"dict1": {"a": 1, "b": 2}, "dict2": {"b": 3, "c": 4}},
        "esperado": {"a": 1, "b": 3, "c": 4}
    },
    {
        "criterio": "Valores do segundo dicionário sobrescrevem valores do primeiro para chaves comuns",
        "entrada": {"dict1": {"a": 1, "b": 2}, "dict2": {"a": 0, "b": 3, "c": 4}},
        "esperado": {"a": 0, "b": 3, "c": 4}
    },
    {
      
```
### 12: e0131 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "numero_por_extenso(0)",
        "entrada": 0,
        "esperado": "zero"
    },
    {
        "criterio": "numero_por_extenso(1)",
        "entrada": 1,
        "esperado": "um"
    },
    {
        "criterio": "numero_por_extenso(10)",
        "entrada": 10,
        "esperado": "dez"
    },
    {
        "criterio": "numero_por_extenso(11)",
        "entrada": 11,
        "esperado": "onze"
    },
    {
        "criterio": "numero_por_extenso(20)",
        "
```
### 13: e0138 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "classificar_status(404)",
        "entrada": 404,
        "esperado": "Not Found"
    },
    {
        "criterio": "classificar_status('200')",
        "entrada": '200',
        "esperado": "Success"
    },
    {
        "criterio": "classificar_status(-1)",
        "entrada": -1,
        "esperado": "ValueError: Código inválido."
    },
    {
        "criterio": "classificar_status(600)",
        "entrada": 600,
        "esperado": "ValueError: Código inváli
```
### 14: e0142 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor deve aceitar valor_inicial (float > 0), vida_util_anos (int > 0) e metodo ('linear', 'soma_digitos' ou 'saldo_declinante') e armazená-los como atributos",
        "entrada": {
            "valor_inicial": 1000,
            "vida_util_anos": 10,
            "metodo": "linear"
        },
        "esperado": null
    },
    {
        "criterio": "O construtor deve levantar ValueError se valor_inicial <= 0, vida_util_anos <= 0 ou metodo inválido",
  
```
### 15: e0164 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "enfileirar(msg)",
        "entrada": {"msg": "mensagem1"},
        "esperado": 1
    },
    {
        "criterio": "desenfileirar()",
        "entrada": {},
        "esperado": ["(1, 'mensagem1')"]
    },
    {
        "criterio": "confirmar(id)",
        "entrada": {"id": 1},
        "esperado": None
    },
    {
        "criterio": "pendentes()",
        "entrada": {},
        "esperado": [
            "(1, 'mensagem1')"
        ]
    }
]
```
```
### 16: e0169 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Adicionar cabeçalho válido",
        "entrada": {"nome": "Content-Type", "valor": "application/json"},
        "esperado": true
    },
    {
        "criterio": "Adicionar cabeçalho com nome vazio",
        "entrada": {"nome": "", "valor": "application/json"},
        "esperado": false
    },
    {
        "criterio": "Adicionar cabeçalho com nome contendo caracteres inválidos",
        "entrada": {"nome": "Header!@#", "valor": "application/json"},
        "e
```
### 17: e0195 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método adicionar aceita qualquer objeto como item e um inteiro como prioridade, inserindo o item na fila ordenado por prioridade (menor valor = maior prioridade)",
        "entrada": {"item": "chocolate", "prioridade": 3},
        "esperado": "True"
    },
    {
        "criterio": "O método adicionar levanta TypeError se a prioridade não for um inteiro",
        "entrada": {"item": "chocolate", "prioridade": "banana"},
        "esperado": "TypeError"
    }
```
### 18: e0200 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função extrair_campos retorna uma lista ordenada de nomes únicos de campos não vazios encontrados entre {{ }}",
        "entrada": "{{nome}} {{sobrenome}}",
        "esperado": ["nome", "sobrenome"]
    },
    {
        "criterio": "A função extrair_campos levanta ValueError quando o template contém chaves desbalanceadas",
        "entrada": "{{nome} {sobrenome}}",
        "esperado": "ValueError"
    },
    {
        "criterio": "A função extrair_campos ig
```
### 19: e0202 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "rotacionar_esquerda(lista, k)",
        "entrada": {"lista": [1, 2, 3, 4], "k": 2},
        "esperado": "[3, 4, 1, 2]"
    },
    {
        "criterio": "rotacionar_esquerda(lista, k)",
        "entrada": {"lista": [], "k": 2},
        "esperado": []
    },
    {
        "criterio": "rotacionar_esquerda(lista, k)",
        "entrada": {"lista": [1, 2, 3, 4], "k": 7},
        "esperado": "[3, 4, 1, 2]"
    },
    {
        "criterio": "rotacionar_direita(lista, 
```
### 20: e0207 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Deve retornar a data de entrega corretamente.",
        "entrada": {"data_inicial": "2023-01-01", "dias_uteis": 7},
        "esperado": "2023-01-08"
    },
    {
        "criterio": "Deve levantar ValueError se a data for inválida.",
        "entrada": {"data_inicial": "invalid-date", "dias_uteis": 7},
        "esperado": "ValueError"
    },
    {
        "criterio": "Deve levantar ValueError se o formato da data for incorreto.",
        "entrada": {"data_ini
```
### 21: e0235 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'vencimentos_por_mes' retorna nomes das contas ordenados alfabeticamente.",
        "entrada": [
            ["conta_a", 1],
            ["conta_b", 20]
        ],
        "esperado": [
            "conta_a",
            "conta_b"
        ]
    },
    {
        "criterio": "A função 'vencimentos_por_mes' levanta ValueError quando o mês é inválido.",
        "entrada": [
            ["conta_c", 13],
            ["conta_d", 32]
        ],
        "espe
```
### 22: e0238 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método adicionar(valor) incrementa a contagem interna quando o valor é igual ao valor adicionado anteriormente",
        "entrada": {"valor": 5},
        "esperado": 1
    },
    {
        "criterio": "O método adicionar(valor) levanta ValueError com mensagem 'Valor não pode ser None' se o argumento for None",
        "entrada": {"valor": None},
        "esperado": "ValueError: Valor não pode ser None"
    },
    {
        "criterio": "O método obter_contag
```
### 23: e0273 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "validar_arquivo retorna True quando tamanho <= 5_000_000 e tipo está na lista permitida",
        "entrada": {
            "nome": "imagem.png",
            "tamanho": 5000000,
            "tipo": "image/png"
        },
        "esperado": true
    },
    {
        "criterio": "validar_arquivo retorna False quando tamanho > 5_000_000 ou tipo não está na lista permitida",
        "entrada": {
            "nome": "texto.txt",
            "tamanho": 5000000,
   
```
### 24: e0282 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método registrar_cesta deve aceitar apenas time 'A' ou 'B' e pontos 1, 2 ou 3.",
        "entrada": {"time": "A", "pontos": "1"},
        "esperado": "ValueError"
    },
    {
        "criterio": "O método registrar_cesta deve levantar ValueError para time inválido ou pontos fora de 1, 2, 3.",
        "entrada": {"time": "X", "pontos": "1"},
        "esperado": "ValueError"
    },
    {
        "criterio": "O método registrar_cesta deve somar pontos ao time
```
### 25: e0284 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função 'calcular_nivel_experiencia' deve retornar uma tupla (nível, xp_para_próximo_nível) corretamente.",
        "entrada": {
            "experiencia_atual": 750,
            "esperado": "(3, 250)"
        }
    },
    {
        "criterio": "A função 'calcular_nivel_experiencia' deve levantar ValueError quando a experiência é negativa.",
        "entrada": {
            "experiencia_atual": -50,
            "esperado": "ValueError"
        }
    },
    {
```
### 26: e0295 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "Retorna 'Jogador 1 venceu' quando o primeiro dado é maior",
        "entrada": {"dado1": 5, "dado2": 3},
        "esperado": "Jogador 1 venceu"
    },
    {
        "critério": "Retorna 'Jogador 2 venceu' quando o segundo dado é maior",
        "entrada": {"dado1": 1, "dado2": 4},
        "esperado": "Jogador 2 venceu"
    },
    {
        "critério": "Retorna 'Empate' quando os dados têm o mesmo valor",
        "entrada": {"dado1": 2, "dado2": 2},
        "e
```
### 27: e0299 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função serializar_registros aceita uma lista de dicionários e retorna uma string com uma linha por registro.",
        "entrada": [
            {"nome": "João", "idade": 30},
            {"cidade": "São Paulo"}
        ],
        "esperado": "{'nome': 'João', 'idade': '30'}, {'cidade': 'São Paulo'}\n"
    },
    {
        "criterio": "Valores do tipo str são envolvidos por aspas duplas e aspas duplas internas são duplicadas.",
        "entrada": [
         
```
### 28: e0301 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "adicionar_registro insere o par chave-valor no dicionário quando a chave não existe",
        "entrada": {"repo": {}, "chave": "chave1", "valor": "valor1"},
        "esperado": None
    },
    {
        "criterio": "adicionar_registro levanta ValueError com mensagem 'Chave já existe no repositório' quando a chave já está presente",
        "entrada": {"repo": {"chave1": "valor1"}, "chave": "chave1", "valor": "novo_valor"},
        "esperado": ValueError("Chav
```
### 29: e0304 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função mesclar_ambientes aceita uma lista de dicionários e retorna um dicionário único mesclado.",
        "entrada": [
            {"nome": "Ambiente 1", "configuracao": {"host": "localhost"}},
            {"nome": "Ambiente 2", "configuracao": {"port": 8080}}
        ],
        "esperado": {
            "nome": "Ambiente 2",
            "configuracao": {
                "host": "localhost",
                "port": 8080
            }
        }
    },
    {
```
### 30: e0312 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor armazena o dicionário inicial como versão 1 e define a versão atual como 1.",
        "entrada": {},
        "esperado": 1
    },
    {
        "criterio": "O método atualizar cria uma nova versão incrementada mesclando as novas chaves sobre a versão anterior e retorna o número da nova versão.",
        "entrada": {"novas_configs": {}},
        "esperado": 2
    },
    {
        "criterio": "O método obter retorna uma cópia do dicionário da versã
```
### 31: e0323 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função ranking_empates deve retornar uma lista de tuplas (posição, nome, pontuação) ordenada por pontuação decrescente.",
        "entrada": [
            ["João", 9],
            ["Maria", 8],
            ["Pedro", 7]
        ],
        "esperado": [
            [1, "João", 9],
            [2, "Maria", 8],
            [3, "Pedro", 7]
        ]
    },
    {
        "criterio": "Se a lista estiver vazia, a função deve levantar ValueError.",
        "entrada"
```
### 32: e0383 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método fazer(acao) adiciona a ação ao final do histórico principal e limpa o histórico de refazer.",
        "entrada": "Editor().fazer('Ação 1')",
        "esperado": ["Ação 1"]
    },
    {
        "criterio": "O método fazer(acao) retorna uma cópia da lista atual do histórico principal.",
        "entrada": "Editor().fazer('Ação 1'), Editor().fazer('Ação 2'),
                   Editor().fazer('Ação 3'), Editor().fazer('Ação 4')",
        "esperado": ["Aç
```
### 33: e0392 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Levanta ValueError quando a sequência de entrada está vazia.",
        "entrada": [],
        "esperado": "ValueError"
    },
    {
        "criterio": "Levanta TypeError quando a sequência contém elementos que não são int ou float.",
        "entrada": [1, "a", 3],
        "esperado": "TypeError"
    },
    {
        "criterio": "Retorna o desvio padrão populacional (raiz quadrada da variância populacional) para sequências válidas com um ou mais elementos.",
```
### 34: e0393 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "graus_para_rad converte graus em radianos multiplicando o valor por pi/180 e retorna float",
        "entrada": {"graus": 90},
        "esperado": 1.5707963267948966
    },
    {
        "criterio": "rad_para_graus converte radianos em graus multiplicando o valor por 180/pi e retorna float",
        "entrada": {"rad": 1.5707963267948966},
        "esperado": 90
    },
    {
        "criterio": "Ambas as funções aceitam int ou float, incluindo valores negativo
```
### 35: e0420 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "n < 2",
        "entrada": 0,
        "esperado": "ValueError"
    },
    {
        "criterio": "n == 2",
        "entrada": 2,
        "esperado": [2]
    },
    {
        "criterio": "n > 2 e n != 2",
        "entrada": 10,
        "esperado": [2, 5]
    }
]
```
```
### 36: e0425 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Se qualquer limite não for inteiro, levante TypeError",
        "entrada": {"inicio": "abc", "fim": 5},
        "esperado": "TypeError"
    },
    {
        "criterio": "Se início for maior que fim, levante ValueError",
        "entrada": {"inicio": 6, "fim": 3},
        "esperado": "ValueError"
    },
    {
        "criterio": "pares_na_faixa deve retornar apenas números pares entre início e fim inclusive",
        "entrada": {"inicio": 0, "fim": 10},
      
```
### 37: e0433 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função pontuacao_final aceita exatamente três argumentos inteiros: acertos, erros e tempo",
        "entrada": {"acertos": 10, "erros": 5, "tempo": 6},
        "esperado": 40
    },
    {
        "criterio": "Se acertos for negativo, levanta ValueError",
        "entrada": {"acertos": -1, "erros": 5, "tempo": 6},
        "erro": "ValueError"
    },
    {
        "criterio": "Se erros for negativo, levanta ValueError",
        "entrada": {"acertos": 10, "err
```
### 38: e0434 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "para_moeda(100)",
        "entrada": "",
        "esperado": "R$ 100,00"
    },
    {
        "criterio": "para_moeda(-100)",
        "entrada": "-100",
        "esperado": "ValueError"
    },
    {
        "criterio": "para_moeda('100.00')",
        "entrada": "100.00",
        "esperado": "R$ 100,00"
    },
    {
        "criterio": "para_moeda('100,00')",
        "entrada": "100,00",
        "esperado": "R$ 100,00"
    },
    {
        "criterio": "para_mo
```
### 39: e0450 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "saque levanta ValueError quando o valor é negativo",
        "entrada": {"valor": -10},
        "esperado": "ValueError"
    },
    {
        "criterio": "saque levanta ValueError quando o valor excede o saldo disponível",
        "entrada": {"valor": 200},
        "esperado": "ValueError"
    },
    {
        "criterio": "saque reduz o saldo pelo valor sacado quando válido",
        "entrada": {"valor": 10},
        "esperado": 90
    },
    {
        "crite
```
### 40: e0455 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Destino inexistente",
        "entrada": {"destino": "Inexistente", "peso": 5},
        "esperado": "ValueError"
    },
    {
        "criterio": "Peso negativo",
        "entrada": {"destino": "Existente", "peso": -1},
        "esperado": "ValueError"
    },
    {
        "criterio": "Tarifa base + preço por kg * peso",
        "entrada": {"destino": "Existente", "peso": 5},
        "esperado": "7.0"
    }
]
```
```
### 41: e0456 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor deve aceitar apenas strings e armazenar a linha para leitura posterior",
        "entrada": "None",
        "esperado": "ValueError"
    },
    {
        "criterio": "Se o construtor receber None ou um valor que não seja string, deve levantar ValueError",
        "entrada": "123",
        "esperado": "ValueError"
    },
    {
        "criterio": "O método ler deve retornar uma lista com os campos separados por vírgula",
        "entrada": "A,B,C\
```
### 42: e0466 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Levanta ValueError se a cesta estiver vazia",
        "entrada": {},
        "esperado": "ValueError"
    },
    {
        "criterio": "Levanta ValueError se algum preço for negativo",
        "entrada": {"precos_negativos": [10, -20]},
        "esperado": "ValueError"
    },
    {
        "criterio": "Levanta ValueError se alguma quantidade for negativa",
        "entrada": {"quantidades_negativas": [-5, 0]},
        "esperado": "ValueError"
    },
    {
   
```
### 43: e0472 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor rejeita versão_inicial menor ou igual a zero ou não inteiro",
        "entrada": {"versao_inicial": -1},
        "esperado": "ValueError"
    },
    {
        "criterio": "aplicar_mudancas rejeita argumentos que não sejam dicionário",
        "entrada": {"mudancas": [1, 2]},
        "esperado": "TypeError"
    },
    {
        "criterio": "aplicar_mudancas atualiza chaves existentes e adiciona novas, retornando o dicionário atualizado",
        "
```
### 44: e0520 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função deve aceitar apenas strings e levantar TypeError para outros tipos",
        "entrada": "contar_palavras_e_frases('Hello world! How are you? I am fine.')",
        "esperado": {"palavras": 6, "frases": 0}
    },
    {
        "criterio": "A função deve levantar ValueError se o texto estiver vazio ou conter apenas espaços",
        "entrada": "contar_palavras_e_frases('')",
        "esperado": {"palavras": 0, "frases": 0}
    },
    {
        "criteri
```
### 45: e0534 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "Se qualquer um dos três argumentos fornecidos não for um dicionário, a função deve levantar ValueError.",
        "entrada": {"config_ambiente": {}, "config_arquivo": {}, "variaveis_de_ambiente": {}},
        "esperado": "ValueError"
    },
    {
        "critério": "O dicionário resultante deve conter todas as chaves únicas presentes nas três camadas de entrada.",
        "entrada": {"config_ambiente": {"chave1": "valor1"}, "config_arquivo": {"chave2": "valo
```
### 46: e0540 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "A classe Classificacao deve permitir adicionar itens.",
        "entrada": [
            {"nome": "item1", "idade": 20},
            {"nome": "item2", "idade": 25}
        ],
        "esperado": ["{'nome': 'item1', 'idade': 20}", "'nome': 'item2', 'idade': 25"]  # Exemplo de saída esperada
    },
    {
        "critério": "O método ordenar deve retornar uma nova lista ordenada.",
        "entrada": [
            [{"nome": "item1", "idade": 20}, {"nome": "item
```
### 47: e0584 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função proximo_estado_pedido deve retornar o próximo estado válido.",
        "entrada": {"estado_atual": "novo", "estado_desejado": "pago"},
        "esperado": "pago"
    },
    {
        "criterio": "A função proximo_estado_pedido deve retornar o próximo estado válido.",
        "entrada": {"estado_atual": "pago", "estado_desejado": "enviado"},
        "esperado": "enviado"
    },
    {
        "criterio": "A função proximo_estado_pedido deve retornar o 
```
### 48: e0587 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "normalizar_vendas",
        "entrada": [
            {"data": "2023-01-15", "vendedor": "João Silva", "valor": 100},
            {"data": "2023-02-28", "vendedor": "Maria Santos", "valor": -50}
        ],
        "esperado": [
            {"data": "2023-01-15", "vendedor": "João Silva", "valor": 100, "mes": "2023-01"},
            {"data": "2023-02-28", "vendedor": "Maria Santos", "valor": -50, "mes": "2023-02"}
        ]
    },
    {
        "critério": "ven
```
### 49: e0614 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Código HTTP deve estar entre 100 e 599",
        "entrada": {"codigo_http": 600},
        "esperado": "ValueError"
    },
    {
        "criterio": "Código HTTP deve ser um número inteiro e não booleano",
        "entrada": {"codigo_http": "abc"},
        "esperado": "ValueError"
    },
    {
        "criterio": "Código HTTP deve ser um número inteiro e maior ou igual a 100",
        "entrada": {"codigo_http": 100},
        "esperado": "Sucesso"
    },
    {

```
### 50: e0619 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O método matricular deve adicionar um aluno com uma nota válida entre 0 e 10.",
        "entrada": {"aluno": "João", "nota": 8},
        "esperado": null
    },
    {
        "criterio": "O método matricular deve atualizar a nota de um aluno já cadastrado.",
        "entrada": {"aluno": "Maria", "nova_nota": 9},
        "esperado": null
    },
    {
        "criterio": "O método matricular deve lançar ValueError se a nota for menor que 0 ou maior que 10.",
  
```
### 51: e0633 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor armazena ano_nascimento e ano_atual como atributos da instância",
        "entrada": {"ano_nascimento": 1980, "ano_atual": 2022},
        "esperado": 42
    },
    {
        "criterio": "O método anos_completos() retorna a diferença entre os anos",
        "entrada": {"ano_nascimento": 1980, "ano_atual": 2022},
        "esperado": 42
    },
    {
        "criterio": "Quando ano_atual é igual a ano_nascimento, o método retorna zero",
        "entr
```
### 52: e0637 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor inicializa o acumulador em zero",
        "entrada": "",
        "esperado": 0
    },
    {
        "criterio": "Validar que raiz é inteiro e não negativo, caso contrário levantar ValueError",
        "entrada": {"raiz": -1},
        "esperado": "ValueError"
    },
    {
        "criterio": "Validar que expoente é inteiro não negativo, caso contrário levantar ValueError",
        "entrada": {"expoente": -1},
        "esperado": "ValueError"
    }
```
### 53: e0639 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A matriz fornecida é quadrada.",
        "entrada": [
            [[1, 2], [3, 4]],
            [[1, 2, 3], [4, 5, 6]]
        ],
        "esperado": [
            [1, 3],
            [3, 6]
        ]
    },
    {
        "criterio": "A matriz fornecida tem mais de uma linha.",
        "entrada": [
            [[1, 2], [3, 4], [5, 6]],
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        ],
        "esperado": [
            ValueError,
            ValueError
```
### 54: e0657 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Depositar um valor positivo soma esse valor ao saldo atual.",
        "entrada": {"estado": {"saldo": 100}, "evento": {"tipo": "depositar", "valor": 50}},
        "esperado": {"estado": {"saldo": 150}}
    },
    {
        "criterio": "Sacar um valor menor ou igual ao saldo subtrai esse valor do saldo.",
        "entrada": {"estado": {"saldo": 100}, "evento": {"tipo": "sacar", "valor": 50}},
        "esperado": {"estado": {"saldo": 50}}
    },
    {
        "
```
### 55: e0662 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "ConversorNumeralRomano.converte_inteiro_para_numeral",
        "entrada": {"numero": 1},
        "esperado": "I"
    },
    {
        "criterio": "ConversorNumeralRomano.converte_inteiro_para_numeral",
        "entrada": {"numero": 10},
        "esperado": "X"
    },
    {
        "criterio": "ConversorNumeralRomano.converte_inteiro_para_numeral",
        "entrada": {"numero": 20},
        "esperado": "XX"
    },
    {
        "criterio": "ConversorNumeralRom
```
### 56: e0687 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A função deve retornar a palavra correspondente para inteiros de 0 a 19.",
        "entrada": 17,
        "esperado": "dez e sete"
    },
    {
        "criterio": "A função deve retornar a palavra da dezena para múltiplos de 10 de 20 a 90.",
        "entrada": 45,
        "esperado": "quatro dez e cinco"
    },
    {
        "criterio": "A função deve retornar 'dezenas e unidade' para números de 21 a 99 que não são múltiplos de 10.",
        "entrada": 68,
 
```
### 57: e0693 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Se a entrada não for uma string, levantar TypeError",
        "entrada": "Não é uma string",
        "esperado": "TypeError"
    },
    {
        "criterio": "Remover espaços no início e no final de cada linha",
        "entrada": "Linha 1\n   Linha 2\nLinha 3\n   Linha 4\nLinha 5",
        "esperado": "Linha 1\nLinha 2\nLinha 3\nLinha 4\nLinha 5"
    },
    {
        "criterio": "Colapsar múltiplos espaços consecutivos dentro de uma linha em um único espaço"
```
### 58: e0702 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "eh_armstrong(153)",
        "entrada": 153,
        "esperado": true
    },
    {
        "criterio": "eh_armstrong(-153)",
        "entrada": -153,
        "erro": "ValueError"
    },
    {
        "criterio": "eh_armstrong('abc')",
        "entrada": 'abc',
        "erro": "ValueError"
    },
    {
        "criterio": "eh_armstrong(987654321)",
        "entrada": 987654321,
        "esperado": false
    },
    {
        "criterio": "eh_armstrong(1)",
      
```
### 59: e0707 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Adicionar cabeçalho com nome normalizado",
        "entrada": {"cabecalho": {"nome": "Content-Type", "valor": "application/json"}},
        "esperado": true
    },
    {
        "criterio": "Remover espaços ao redor do valor",
        "entrada": {"cabecalho": {"nome": "Content-Length", "valor": " 1000 "}},
        "esperado": true
    },
    {
        "criterio": "Consultar cabeçalho por nome (case-insensitive)",
        "entrada": {"cabecalho": {"nome": "con
```
### 60: e0708 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Salário base negativo levanta ValueError",
        "entrada": {"salario_base": -100},
        "esperado": "ValueError"
    },
    {
        "criterio": "Horas extras negativas levanta ValueError",
        "entrada": {"horas_extras": -5},
        "esperado": "ValueError"
    },
    {
        "criterio": "Valor da hora normal calculado corretamente",
        "entrada": {"salario_base": 1000},
        "esperado": 45.45
    },
    {
        "criterio": "Horas ext
```
### 61: e0714 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Adicionar um item com lista de chaves vazia levanta ValueError no momento da adição",
        "entrada": {"item": "valor", "chaves": []},
        "esperado": "ValueError"
    },
    {
        "criterio": "Chamar classificar() sem nenhum item adicionado levanta ValueError",
        "entrada": {},
        "esperado": "ValueError"
    }
]
```
```
### 62: e0734 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "validar_dependencias",
        "entrada": {"servicos": {"servicoA": ["servicoB"], "servicoB": [], "servicoC": ["servicoD"]}},
        "esperado": "ValueError"
    },
    {
        "criterio": "validar_dependencias",
        "entrada": {"servicos": {"servicoA": ["servicoB", "servicoC"], "servicoB": ["servicoA"], "servicoC": []}},
        "esperado": "ValueError"
    },
    {
        "criterio": "validar_dependencias",
        "entrada": {"servicos": {"servicoA
```
### 63: e0737 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "O construtor deve levantar ValueError quando defaults não for um dicionário",
        "entrada": {},
        "esperado": "ValueError"
    },
    {
        "criterio": "A chave encontrada apenas em defaults deve ser retornada dos valores padrão",
        "entrada": {"chave": "valor"},
        "esperado": "None" // Não há valores padrão para essa chave
    },
    {
        "criterio": "A chave encontrada em arquivo deve ser retornada mesmo que também exista em 
```
### 64: e0749 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "adicionar(valor) aceita apenas int ou float e levanta TypeError para outros tipos",
        "entrada": {"valor": 1},
        "esperado": null
    },
    {
        "criterio": "adicionar(valor) retorna None após registrar o valor",
        "entrada": {"valor": 1},
        "esperado": null
    },
    {
        "criterio": "adicionar(valor) acumula a contagem quando o mesmo valor é adicionado múltiplas vezes",
        "entrada": [{"valor": 1}, {"valor": 1}],
   
```
### 65: e0759 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "adicionar",
        "entrada": {"item": "banana"},
        "esperado": ["banana"]
    },
    {
        "criterio": "particionar",
        "entrada": {"critério": lambda x: True},
        "esperado": [
            {"aceitos": ["banana"], "rejeitados": []}
        ]
    },
    {
        "criterio": "particionar",
        "entrada": {"critério": lambda x: False},
        "esperado": [
            {"aceitos": [], "rejeitados": ["banana"]}
        ]
    },
    {
 
```
### 66: e0771 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "normalizar_cpf remove todos os caracteres que não são dígitos da entrada",
        "entrada": "12345678901",
        "esperado": "12345678901"
    },
    {
        "criterio": "normalizar_cpf levanta ValueError quando a entrada não contém exatamente 11 dígitos numéricos",
        "entrada": "1234567890",
        "esperado": "ValueError"
    },
    {
        "criterio": "normalizar_cpf levanta ValueError quando todos os 11 dígitos são iguais",
        "entrada
```
### 67: e0781 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "calcular_pontos deve retornar 3 quando gols_pro for maior que gols_contra",
        "entrada": {"gols_pro": 5, "gols_contra": 3},
        "esperado": 3
    },
    {
        "criterio": "calcular_pontos deve retornar 1 quando gols_pro for igual a gols_contra",
        "entrada": {"gols_pro": 4, "gols_contra": 4},
        "esperado": 1
    },
    {
        "criterio": "calcular_pontos deve retornar 0 quando gols_pro for menor que gols_contra",
        "entrada"
```
### 68: e0791 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "disparar_tiros",
        "entrada": [
            [(0, 0), (1, 1)],
            [(1, 0), (0, 1)]
        ],
        "esperado": [
            {0: [0], 1: [1]},
            {0: [], 1: []}
        ]
    },
    {
        "criterio": "disparar_tiros",
        "entrada": [
            [(0, 0), (1, 1), (1, 1)],
            [(1, 0), (0, 1)]
        ],
        "esperado": [
            {0: [0], 1: [1]},
            {0: [], 1: []}
        ]
    },
    {
        "crite
```
### 69: e0815 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "A classe ComissaoVendas deve calcular corretamente a comissão de vendas.",
        "entrada": {
            "valor_venda": -1000,
            "comissao_abaixo_de_1000": 5,
            "comissao_entre_1000_e_5000_inclusivo": 10,
            "comissao_acima_de_5000": 15
        },
        "esperado": "ValueError"
    },
    {
        "criterio": "Se o valor da venda for menor que 1000, a comissão deve ser de 5%",
        "entrada": {
            "valor_venda": 
```
### 70: e0816 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Matrícula está dentro do intervalo permitido",
        "entrada": {"matricula": 100000000},
        "esperado": ValueError("Matrícula inválida")
    },
    {
        "criterio": "Nota está dentro do intervalo permitido",
        "entrada": {"nota": -5},
        "esperado": ValueError("Nota inválida")
    },
    {
        "criterio": "Aluno com média maior aparece primeiro no ranking",
        "entrada": {"turma": [{"nome": "João", "notas": [8, 7]}, {"nome": "
```
### 71: q0031 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Devolve uma lista com os valores presentes nas três listas, em ordem crescente.",
        "entrada": [
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5]
        ],
        "esperado": "[1, 2, 3, 4, 5]"
    },
    {
        "criterio": "Valores repetidos em qualquer das listas aparecem uma única vez no resultado.",
        "entrada": [
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5, 2]
        ],
        "esperado": "[1, 2
```
### 72: q0069 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "contar_ilhas deve retornar 0 quando a matriz está vazia",
        "entrada": [],
        "esperado": 0
    },
    {
        "criterio": "contar_ilhas deve retornar 0 quando a matriz não tem nenhum 1",
        "entrada": [[], [0]],
        "esperado": 0
    },
    {
        "criterio": "contar_ilhas deve retornar a quantidade de grupos de 1 conectados na horizontal/vertical",
        "entrada": [
            [1, 1, 0],
            [1, 0, 1],
            [0, 1,
```
### 73: q0051 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "valor_noite('simples')",
        "entrada": "",
        "esperado": 120.0
    },
    {
        "criterio": "valor_noite('duplo')",
        "entrada": "",
        "esperado": 180.0
    },
    {
        "criterio": "valor_noite('suite')",
        "entrada": "",
        "esperado": 300.0
    },
    {
        "criterio": "valor_noite('luxo')",
        "entrada": "",
        "esperado": 450.0
    },
    {
        "criterio": "valor_noite('quarto_inexistente')",
  
```
### 74: q0077 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "critério": "A instância nova começa com total igual a 0.",
        "entrada": "",
        "esperado": 0
    },
    {
        "critério": "Cada dígito de 1 a 6 na string soma o seu valor ao total.",
        "entrada": "123",
        "esperado": 18
    },
    {
        "critério": "Cada caractere 'd' na string dobra o total acumulado até aquele ponto.",
        "entrada": "12dd3",
        "esperado": 27
    },
    {
        "critério": "O método processar devolve o total f
```
### 75: q0063 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "Devolve uma lista de tuplas (inicio, fim, quantidade) em ordem crescente de inicio, começando em 0, com faixas de largura igual a tamanho.",
        "entrada": [
            ["[1, 2, 3]", 1],
            ["[4, 5, 6, 7, 8]", 2]
        ],
        "esperado": [
            ["(0, 1, 1)", "(1, 2, 1)", "(2, 3, 1)"],
            ["(0, 2, 3)", "(2, 4, 2)"]
        ]
    },
    {
        "criterio": "A última faixa termina no menor fim possível que seja maior ou igua
```
### 76: q0055 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "intercalar deve retornar uma lista com os elementos de a e b alternados",
        "entrada": [
            ["a", [1, 2, 3]],
            ["b", [4, 5, 6]]
        ],
        "esperado": [[1, 4], [2, 5], [3, 6]]
    },
    {
        "criterio": "intercalar deve levantar ValueError quando as listas têm tamanhos diferentes",
        "entrada": [
            ["a", [1, 2, 3]],
            ["b", [4, 5]]
        ],
        "esperado": "ValueError"
    },
    {
      
```
### 77: q0038 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "inserir adiciona o valor e em_ordem devolve a lista dos valores em ordem crescente",
        "entrada": {"valor": 5},
        "esperado": [5]
    },
    {
        "criterio": "inserir ignora valores duplicados, mantendo uma única ocorrência em em_ordem",
        "entrada": {"valor": 5},
        "esperado": [5]
    },
    {
        "criterio": "buscar devolve True quando o valor está na árvore e False quando não está",
        "entrada": {"valor": 5},
        
```
### 78: q0064 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "em_ordem(None) devolve uma lista vazia.",
        "entrada": "",
        "esperado": []
    },
    {
        "criterio": "inserir(None, valor) cria uma árvore cujo percurso em ordem é a lista com apenas esse valor.",
        "entrada": {"raiz": None, "valor": 7},
        "esperado": [7]
    },
    {
        "criterio": "Inserir valores em ordem arbitrária faz em_ordem devolver a lista ordenada crescente desses valores.",
        "entrada": [
            {"rai
```
### 79: q0017 | formato INVÁLIDO | plano inválido | notas: 0 corretos, 0 errados, 0 inavaliáveis
```
```json
[
    {
        "criterio": "acrescentadas",
        "entrada": ["banana", "maçã", "laranja"],
        "esperado": [
            "kiwi"
        ]
    },
    {
        "criterio": "removidas",
        "entrada": ["banana", "maçã", "laranja"],
        "esperado": [
            "kiwi"
        ]
    },
    {
        "criterio": "mantidas",
        "entrada": ["banana", "kiwi", "laranja"],
        "esperado": [
            "maçã"
        ]
    }
]
```
```
"""Solução de referência (correta) de cada tarefa do conjunto fácil: id -> {arquivo: conteúdo}.

Servem de oráculo: o código do agente e os testes que ele escreveu são conferidos contra elas.
Cada referência é validada contra o verificador oculto da tarefa em validar_referencias.py.
"""

REFERENCIAS_FACEIS = {
    1: {"fatorial.py": '''def fatorial(n):
    if n < 0:
        raise ValueError("n não pode ser negativo")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado
'''},
    2: {"palindromo.py": '''def eh_palindromo(texto):
    limpo = texto.lower().replace(" ", "")
    return limpo == limpo[::-1]
'''},
    3: {"fib.py": '''def fibonacci(n):
    if n < 0:
        raise ValueError("n não pode ser negativo")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
'''},
    4: {"contagem.py": '''def contar_palavras(texto):
    contagem = {}
    for palavra in texto.lower().split():
        contagem[palavra] = contagem.get(palavra, 0) + 1
    return contagem
'''},
    5: {"calc.py": '''def media(lista):
    return sum(lista) / len(lista)
'''},
    6: {"lista.py": '''def maior(lista):
    resultado = lista[0]
    for x in lista:
        if x > resultado:
            resultado = x
    return resultado
'''},
    7: {"numeros.py": '''def eh_par(n):
    return n % 2 == 0
'''},
    8: {"saudacao.py": '''def saudacao(nome, formal=False):
    if formal:
        return f'Prezado(a) {nome}'
    return f'Olá, {nome}'
'''},
    9: {"preco.py": '''def preco_final(preco, desconto=0):
    return preco * (1 - desconto / 100)
'''},
    10: {"tests/test_estoque.py": '''from estoque import adicionar


def test_adiciona_item_novo():
    assert adicionar({}, "a", 3) == {"a": 3}


def test_soma_em_item_existente():
    assert adicionar({"a": 2}, "a", 3) == {"a": 5}


def test_mantem_outros_itens():
    assert adicionar({"a": 2}, "b", 1) == {"a": 2, "b": 1}


def test_devolve_o_mesmo_dicionario():
    estoque = {}
    assert adicionar(estoque, "a", 1) is estoque


def test_quantidade_zero():
    assert adicionar({}, "a", 0) == {"a": 0}
'''},
    11: {"tests/test_primos.py": '''from primos import eh_primo


def test_primos_pequenos():
    assert eh_primo(2) is True
    assert eh_primo(3) is True
    assert eh_primo(13) is True


def test_compostos():
    assert eh_primo(4) is False
    assert eh_primo(9) is False
    assert eh_primo(100) is False


def test_zero_um_e_negativos():
    assert eh_primo(0) is False
    assert eh_primo(1) is False
    assert eh_primo(-7) is False


def test_primo_grande():
    assert eh_primo(97) is True


def test_quadrado_de_primo():
    assert eh_primo(49) is False
'''},
    12: {"usuario.py": '''def criar_usuario(nome, idade):
    if not nome:
        raise ValueError("nome vazio")
    if idade < 0 or idade > 150:
        raise ValueError("idade fora do intervalo")
    return {'nome': nome, 'idade': idade}
'''},
    13: {"email_utils.py": '''def validar_email(email):
    if email.count("@") != 1:
        return False
    usuario, dominio = email.split("@")
    return bool(usuario) and "." in dominio and not dominio.startswith(".") and not dominio.endswith(".")
'''},
    14: {"area.py": '''def area_retangulo(a, b):
    return a * b


def area_quadrado(l):
    return area_retangulo(l, l)
'''},
    15: {"texto.py": '''def maiusculas_lista(lista):
    return [item.upper() for item in lista]
'''},
}

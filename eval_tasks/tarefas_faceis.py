"""Tarefas de avaliação com verificadores ocultos (testes que o agente nunca vê)."""
import re
import subprocess
import sys


def oculto(codigo):
    # verificador: roda um arquivo de teste que o agente nunca viu
    def verificar(raiz):
        (raiz / "test_oculto.py").write_text(codigo, encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "test_oculto.py"],
                           cwd=raiz, capture_output=True, text=True, timeout=60)
        return r.returncode == 0
    return verificar


def pelo_menos_testes(arquivo_fonte, minimo):
    # verificador para "criar testes": o agente criou ao menos N funções de teste novas
    def verificar(raiz):
        total = 0
        for t in (raiz / "tests").glob("test_*.py") if (raiz / "tests").exists() else []:
            if t.name != "test_original.py":
                total += len(re.findall(r"^\s*def test_", t.read_text(encoding="utf-8"), re.M))
        for t in raiz.glob("test_*.py"):
            if t.name != "test_oculto.py":
                total += len(re.findall(r"^\s*def test_", t.read_text(encoding="utf-8"), re.M))
        return total >= minimo
    return verificar


def e_refatorado(arquivo, padrao, testes_ocultos):
    def verificar(raiz):
        codigo = (raiz / arquivo).read_text(encoding="utf-8")
        return bool(re.search(padrao, codigo, re.S)) and oculto(testes_ocultos)(raiz)
    return verificar


TAREFAS = [
    # ---------- implementar função ----------
    dict(id=1, tipo="implementar", nome="fatorial",
         tarefa="Crie uma função fatorial(n) no arquivo fatorial.py. Para n negativo deve levantar ValueError.",
         arquivos={},
         verificar=oculto("from fatorial import fatorial\nimport pytest\n\ndef test_a():\n    assert fatorial(5) == 120\n    assert fatorial(0) == 1\n    assert fatorial(1) == 1\n\ndef test_b():\n    with pytest.raises(ValueError):\n        fatorial(-1)\n")),
    dict(id=2, tipo="implementar", nome="palindromo",
         tarefa="Crie uma função eh_palindromo(texto) em palindromo.py que devolva True se o texto é um palíndromo, ignorando maiúsculas, minúsculas e espaços.",
         arquivos={},
         verificar=oculto("from palindromo import eh_palindromo\n\ndef test_a():\n    assert eh_palindromo('arara') is True\n    assert eh_palindromo('Socorram me subi no onibus em Marrocos') is True\n\ndef test_b():\n    assert eh_palindromo('python') is False\n    assert eh_palindromo('') is True\n")),
    dict(id=3, tipo="implementar", nome="fibonacci",
         tarefa="Crie uma função fibonacci(n) em fib.py que devolva o n-ésimo número de Fibonacci, com fibonacci(0) == 0 e fibonacci(1) == 1. Para n negativo levante ValueError.",
         arquivos={},
         verificar=oculto("from fib import fibonacci\nimport pytest\n\ndef test_a():\n    assert [fibonacci(i) for i in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]\n\ndef test_b():\n    with pytest.raises(ValueError):\n        fibonacci(-3)\n")),
    dict(id=4, tipo="implementar", nome="contar palavras",
         tarefa="Crie uma função contar_palavras(texto) em contagem.py que devolva um dicionário com a frequência de cada palavra, em minúsculas, separando por espaços.",
         arquivos={},
         verificar=oculto("from contagem import contar_palavras\n\ndef test_a():\n    assert contar_palavras('a b a') == {'a': 2, 'b': 1}\n    assert contar_palavras('Casa casa CASA') == {'casa': 3}\n\ndef test_b():\n    assert contar_palavras('') == {}\n")),
    # ---------- corrigir bug ----------
    dict(id=5, tipo="bug", nome="media",
         tarefa="Os testes de media estão falhando. Descubra e corrija o problema em calc.py.",
         arquivos={"calc.py": "def media(lista):\n    return sum(lista) / len(lista) + 1\n",
                   "tests/test_original.py": "from calc import media\n\ndef test_media():\n    assert media([1, 2, 3]) == 2\n"},
         verificar=oculto("from calc import media\n\ndef test_a():\n    assert media([2, 4]) == 3\n    assert media([5]) == 5\n")),
    dict(id=6, tipo="bug", nome="maior de negativos",
         tarefa="A função maior em lista.py devolve o valor errado para listas só com números negativos. Corrija o bug.",
         arquivos={"lista.py": "def maior(lista):\n    resultado = 0\n    for x in lista:\n        if x > resultado:\n            resultado = x\n    return resultado\n",
                   "tests/test_original.py": "from lista import maior\n\ndef test_positivos():\n    assert maior([1, 9, 3]) == 9\n"},
         verificar=oculto("from lista import maior\n\ndef test_a():\n    assert maior([-3, -1, -2]) == -1\n    assert maior([4]) == 4\n    assert maior([1, 9, 3]) == 9\n")),
    dict(id=7, tipo="bug", nome="eh_par invertido",
         tarefa="Os testes de eh_par estão falhando. Descubra e corrija o problema em numeros.py.",
         arquivos={"numeros.py": "def eh_par(n):\n    return n % 2 == 1\n",
                   "tests/test_original.py": "from numeros import eh_par\n\ndef test_par():\n    assert eh_par(4) is True\n    assert eh_par(7) is False\n"},
         verificar=oculto("from numeros import eh_par\n\ndef test_a():\n    assert eh_par(0) is True\n    assert eh_par(10) is True\n    assert eh_par(3) is False\n")),
    # ---------- modificar API ----------
    dict(id=8, tipo="api", nome="saudacao formal",
         tarefa="Na função saudacao de saudacao.py, adicione o parâmetro opcional formal (padrão False). Com formal=True deve devolver 'Prezado(a) <nome>'. Sem ele, o comportamento atual deve continuar.",
         arquivos={"saudacao.py": "def saudacao(nome):\n    return f'Olá, {nome}'\n",
                   "tests/test_original.py": "from saudacao import saudacao\n\ndef test_padrao():\n    assert saudacao('Ana') == 'Olá, Ana'\n"},
         verificar=oculto("from saudacao import saudacao\n\ndef test_a():\n    assert saudacao('Ana') == 'Olá, Ana'\n    assert saudacao('Ana', formal=True) == 'Prezado(a) Ana'\n    assert saudacao('Bia', False) == 'Olá, Bia'\n")),
    dict(id=9, tipo="api", nome="desconto",
         tarefa="Na função preco_final de preco.py, adicione o parâmetro opcional desconto (percentual, padrão 0) que reduz o preço. Sem desconto o resultado atual deve continuar igual.",
         arquivos={"preco.py": "def preco_final(preco):\n    return preco\n",
                   "tests/test_original.py": "from preco import preco_final\n\ndef test_sem_desconto():\n    assert preco_final(100) == 100\n"},
         verificar=oculto("from preco import preco_final\n\ndef test_a():\n    assert preco_final(100) == 100\n    assert preco_final(100, desconto=10) == 90\n    assert preco_final(200, 50) == 100\n")),
    # ---------- criar testes ----------
    dict(id=10, tipo="criar testes", nome="testes de estoque",
         tarefa="Crie testes para o módulo estoque.py, cobrindo a função adicionar.",
         arquivos={"estoque.py": "def adicionar(estoque, item, qtd):\n    estoque[item] = estoque.get(item, 0) + qtd\n    return estoque\n"},
         verificar=pelo_menos_testes("estoque.py", 2)),
    dict(id=11, tipo="criar testes", nome="testes de primo",
         tarefa="Crie testes para a função eh_primo do módulo primos.py.",
         arquivos={"primos.py": "def eh_primo(n):\n    if n < 2:\n        return False\n    for i in range(2, int(n ** 0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n"},
         verificar=pelo_menos_testes("primos.py", 3)),
    # ---------- validação de dados ----------
    dict(id=12, tipo="validacao", nome="criar_usuario",
         tarefa="Faça criar_usuario, em usuario.py, validar os dados: o nome não pode ser vazio e a idade deve estar entre 0 e 150. Nos casos inválidos deve levantar ValueError.",
         arquivos={"usuario.py": "def criar_usuario(nome, idade):\n    return {'nome': nome, 'idade': idade}\n",
                   "tests/test_original.py": "from usuario import criar_usuario\n\ndef test_valido():\n    assert criar_usuario('Ana', 30) == {'nome': 'Ana', 'idade': 30}\n"},
         verificar=oculto("from usuario import criar_usuario\nimport pytest\n\ndef test_a():\n    assert criar_usuario('Ana', 0)['idade'] == 0\n    assert criar_usuario('Ana', 150)['idade'] == 150\n\ndef test_b():\n    for nome, idade in [('', 20), ('Ana', -1), ('Ana', 151)]:\n        with pytest.raises(ValueError):\n            criar_usuario(nome, idade)\n")),
    dict(id=13, tipo="validacao", nome="validar_email",
         tarefa="Crie uma função validar_email(email) em email_utils.py que devolva True se o email tem exatamente um @, texto antes do @ e um domínio com ponto depois dele; senão False.",
         arquivos={},
         verificar=oculto("from email_utils import validar_email\n\ndef test_a():\n    assert validar_email('ana@exemplo.com') is True\n    assert validar_email('a.b@mail.org') is True\n\ndef test_b():\n    for e in ['', 'ana', 'ana@', '@exemplo.com', 'ana@exemplo', 'a@@b.com']:\n        assert validar_email(e) is False\n")),
    # ---------- refatoração ----------
    dict(id=14, tipo="refatorar", nome="area reutiliza",
         tarefa="Refatore area.py: a função area_quadrado deve reutilizar area_retangulo, sem mudar o comportamento.",
         arquivos={"area.py": "def area_retangulo(a, b):\n    return a * b\n\n\ndef area_quadrado(l):\n    return l * l\n",
                   "tests/test_original.py": "from area import area_quadrado, area_retangulo\n\ndef test_areas():\n    assert area_retangulo(2, 3) == 6\n    assert area_quadrado(4) == 16\n"},
         verificar=e_refatorado("area.py", r"def area_quadrado.*area_retangulo\(",
                                "from area import area_quadrado, area_retangulo\n\ndef test_a():\n    assert area_quadrado(5) == 25\n    assert area_retangulo(2, 7) == 14\n")),
    dict(id=15, tipo="refatorar", nome="list comprehension",
         tarefa="Refatore a função maiusculas_lista de texto.py para usar uma list comprehension, mantendo o comportamento.",
         arquivos={"texto.py": "def maiusculas_lista(lista):\n    resultado = []\n    for item in lista:\n        resultado.append(item.upper())\n    return resultado\n",
                   "tests/test_original.py": "from texto import maiusculas_lista\n\ndef test_maiusculas():\n    assert maiusculas_lista(['a', 'bc']) == ['A', 'BC']\n"},
         verificar=e_refatorado("texto.py", r"\[[^\]]* for [^\]]* in ",
                                "from texto import maiusculas_lista\n\ndef test_a():\n    assert maiusculas_lista(['ab', 'Cd']) == ['AB', 'CD']\n    assert maiusculas_lista([]) == []\n")),
]

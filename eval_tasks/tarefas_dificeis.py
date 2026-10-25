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


def refatorou_precos(raiz):
    codigo = (raiz / "precos.py").read_text(encoding="utf-8")
    comportamento = oculto('''from precos import preco_com_imposto, preco_com_desconto, preco_final

def test_imposto():
    assert preco_com_imposto(100, 0.1) == 110.0

def test_desconto():
    assert preco_com_desconto(200, 25) == 150.0

def test_final():
    assert preco_final(100, 0.1, 10) == 99.0
''')
    # a função auxiliar existe e é o único lugar com round(
    return "def arredondar_moeda" in codigo and codigo.count("round(") == 1 and comportamento(raiz)


TAREFAS = [
    dict(id=1, tipo="varios arquivos", nome="remover usuario (repo + servico)",
         tarefa="Adicione ao RepositorioUsuarios, em repositorio.py, o método remover(id), e adicione ao ServicoUsuarios, em servico.py, o método excluir_usuario(id), que usa remover e levanta KeyError se o usuário não existir.",
         arquivos={
             "repositorio.py": '''class RepositorioUsuarios:
    def __init__(self):
        self._dados = {}

    def adicionar(self, id, nome):
        self._dados[id] = nome

    def obter(self, id):
        return self._dados.get(id)
''',
             "servico.py": '''from repositorio import RepositorioUsuarios


class ServicoUsuarios:
    def __init__(self, repo=None):
        self.repo = repo or RepositorioUsuarios()

    def criar_usuario(self, id, nome):
        self.repo.adicionar(id, nome)
        return nome
''',
             "tests/test_original.py": '''from servico import ServicoUsuarios

def test_criar():
    s = ServicoUsuarios()
    s.criar_usuario(1, "Ana")
    assert s.repo.obter(1) == "Ana"
''',
         },
         verificar=oculto('''import pytest
from repositorio import RepositorioUsuarios
from servico import ServicoUsuarios

def test_remover():
    r = RepositorioUsuarios()
    r.adicionar(1, "Ana")
    r.remover(1)
    assert r.obter(1) is None

def test_excluir():
    s = ServicoUsuarios()
    s.criar_usuario(1, "Ana")
    s.excluir_usuario(1)
    assert s.repo.obter(1) is None

def test_excluir_inexistente():
    s = ServicoUsuarios()
    with pytest.raises(KeyError):
        s.excluir_usuario(99)
''')),
    dict(id=2, tipo="bug sutil", nome="mesclar intervalos",
         tarefa="A função mesclar em intervalos.py tem bugs: ela não une intervalos que se tocam (como (1, 3) e (3, 5)) e não funciona quando a lista vem fora de ordem. Corrija sem estragar o que já funciona.",
         arquivos={
             "intervalos.py": '''def mesclar(intervalos):
    resultado = []
    for inicio, fim in intervalos:
        if resultado and inicio < resultado[-1][1]:
            resultado[-1] = (resultado[-1][0], max(resultado[-1][1], fim))
        else:
            resultado.append((inicio, fim))
    return resultado
''',
             "tests/test_original.py": '''from intervalos import mesclar

def test_basico():
    assert mesclar([(1, 3), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]
''',
         },
         verificar=oculto('''from intervalos import mesclar

def test_basico():
    assert mesclar([(1, 3), (2, 6), (8, 10)]) == [(1, 6), (8, 10)]

def test_se_tocam():
    assert mesclar([(1, 3), (3, 5)]) == [(1, 5)]

def test_fora_de_ordem():
    assert mesclar([(8, 10), (1, 3), (3, 5)]) == [(1, 5), (8, 10)]

def test_vazio():
    assert mesclar([]) == []
''')),
    dict(id=3, tipo="classe com estado", nome="carrinho",
         tarefa="Crie em carrinho.py a classe Carrinho com: adicionar(item, preco, qtd=1), que levanta ValueError se qtd <= 0 ou preco < 0; remover(item), que levanta KeyError se o item não está no carrinho; e total(), que soma preco * qtd de todos os itens. Adicionar o mesmo item de novo soma a quantidade.",
         arquivos={},
         verificar=oculto('''import pytest
from carrinho import Carrinho

def test_total():
    c = Carrinho()
    c.adicionar("a", 10.0, 2)
    c.adicionar("b", 5.0)
    assert c.total() == 25.0

def test_mesmo_item_soma_quantidade():
    c = Carrinho()
    c.adicionar("a", 10.0)
    c.adicionar("a", 10.0, 2)
    assert c.total() == 30.0

def test_remover():
    c = Carrinho()
    c.adicionar("a", 10.0)
    c.remover("a")
    assert c.total() == 0

def test_erros():
    c = Carrinho()
    with pytest.raises(ValueError):
        c.adicionar("a", 10.0, 0)
    with pytest.raises(ValueError):
        c.adicionar("a", -1.0)
    with pytest.raises(KeyError):
        c.remover("x")
''')),
    dict(id=4, tipo="arquivos", nome="contar linhas e palavras",
         tarefa="Crie em arquivos_texto.py duas funções: contar_linhas(caminho), que devolve quantas linhas não vazias o arquivo tem, e palavras_unicas(caminho), que devolve a lista ordenada das palavras distintas do arquivo, em minúsculas, separadas por espaço ou quebra de linha. Se o arquivo não existir, as duas devem levantar FileNotFoundError.",
         arquivos={},
         verificar=oculto('''import pytest
from arquivos_texto import contar_linhas, palavras_unicas

def test_contar(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("um\\n\\ndois tres\\nquatro\\n", encoding="utf-8")
    assert contar_linhas(str(f)) == 3

def test_palavras(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("Casa casa\\nSol lua SOL\\n", encoding="utf-8")
    assert palavras_unicas(str(f)) == ["casa", "lua", "sol"]

def test_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        contar_linhas(str(tmp_path / "x.txt"))
    with pytest.raises(FileNotFoundError):
        palavras_unicas(str(tmp_path / "x.txt"))
''')),
    dict(id=5, tipo="usa codigo existente", nome="perimetro",
         tarefa="Em geometria.py, crie a função perimetro(pontos) que usa a função distancia já existente para somar os lados do polígono formado pelos pontos, ligando o último ponto ao primeiro. Com menos de 3 pontos, levante ValueError.",
         arquivos={
             "geometria.py": '''import math


def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
''',
             "tests/test_original.py": '''from geometria import distancia

def test_distancia():
    assert distancia((0, 0), (3, 4)) == 5.0
''',
         },
         verificar=oculto('''import pytest
from geometria import perimetro

def test_triangulo():
    assert perimetro([(0, 0), (3, 0), (3, 4)]) == pytest.approx(12.0)

def test_quadrado():
    assert perimetro([(0, 0), (2, 0), (2, 2), (0, 2)]) == pytest.approx(8.0)

def test_poucos_pontos():
    with pytest.raises(ValueError):
        perimetro([(0, 0), (1, 1)])
''')),
    dict(id=6, tipo="refatorar", nome="arredondar_moeda",
         tarefa="Refatore precos.py: crie a função auxiliar arredondar_moeda(valor), que arredonda para 2 casas decimais, e use-a no lugar de todos os round(..., 2) das funções existentes, sem mudar o comportamento.",
         arquivos={
             "precos.py": '''def preco_com_imposto(preco, taxa):
    return round(preco * (1 + taxa), 2)


def preco_com_desconto(preco, percentual):
    return round(preco * (1 - percentual / 100), 2)


def preco_final(preco, taxa, percentual):
    return round(preco_com_desconto(preco, percentual) * (1 + taxa), 2)
''',
             "tests/test_original.py": '''from precos import preco_com_imposto, preco_com_desconto, preco_final

def test_precos():
    assert preco_com_imposto(100, 0.1) == 110.0
    assert preco_com_desconto(200, 25) == 150.0
    assert preco_final(100, 0.1, 10) == 99.0
''',
         },
         verificar=refatorou_precos),
    dict(id=7, tipo="modificar API", nome="filtros em listar",
         tarefa="Em tarefas.py, a função listar(tarefas) devolve todas as tarefas (dicionários com as chaves 'titulo', 'feita' e 'prioridade'). Adicione os parâmetros opcionais apenas_pendentes=False, que omite as tarefas feitas, e prioridade=None, que mantém só as tarefas com essa prioridade. Sem eles o comportamento atual deve continuar.",
         arquivos={
             "tarefas.py": '''def listar(tarefas):
    return list(tarefas)
''',
             "tests/test_original.py": '''from tarefas import listar

def test_listar_tudo():
    dados = [{"titulo": "a", "feita": False, "prioridade": 1}]
    assert listar(dados) == dados
''',
         },
         verificar=oculto('''from tarefas import listar

DADOS = [
    {"titulo": "a", "feita": False, "prioridade": 1},
    {"titulo": "b", "feita": True, "prioridade": 2},
    {"titulo": "c", "feita": False, "prioridade": 2},
]

def test_sem_filtros():
    assert listar(DADOS) == DADOS

def test_apenas_pendentes():
    assert [t["titulo"] for t in listar(DADOS, apenas_pendentes=True)] == ["a", "c"]

def test_prioridade():
    assert [t["titulo"] for t in listar(DADOS, prioridade=2)] == ["b", "c"]

def test_os_dois():
    assert [t["titulo"] for t in listar(DADOS, apenas_pendentes=True, prioridade=2)] == ["c"]
''')),
    dict(id=8, tipo="validacao", nome="validar_senha",
         tarefa="Crie em senha.py a função validar_senha(senha) que devolve a lista de regras violadas, usando estes códigos: 'curta' (menos de 8 caracteres), 'sem_digito', 'sem_maiuscula', 'sem_minuscula' e 'com_espaco'. Uma senha válida devolve a lista vazia.",
         arquivos={},
         verificar=oculto('''from senha import validar_senha

def test_valida():
    assert validar_senha("Abcdefg1") == []

def test_curta():
    assert "curta" in validar_senha("Ab1")

def test_varias_regras():
    assert set(validar_senha("abc def")) == {"curta", "sem_digito", "sem_maiuscula", "com_espaco"}

def test_sem_minuscula():
    assert validar_senha("ABCDEFG1") == ["sem_minuscula"]
''')),
    dict(id=9, tipo="bug em classe", nome="pilha",
         tarefa="Os testes da Pilha em pilha.py estão falhando. Descubra e corrija o problema. Desempilhar ou consultar o topo de uma pilha vazia deve levantar IndexError.",
         arquivos={
             "pilha.py": '''class Pilha:
    def __init__(self):
        self.itens = []

    def empilhar(self, item):
        self.itens.append(item)

    def desempilhar(self):
        return self.itens.pop(0)

    def topo(self):
        return self.itens[0]

    def tamanho(self):
        return len(self.itens)
''',
             "tests/test_original.py": '''from pilha import Pilha

def test_lifo():
    p = Pilha()
    p.empilhar(1)
    p.empilhar(2)
    assert p.topo() == 2
    assert p.desempilhar() == 2
    assert p.desempilhar() == 1
''',
         },
         verificar=oculto('''import pytest
from pilha import Pilha

def test_lifo():
    p = Pilha()
    for x in (1, 2, 3):
        p.empilhar(x)
    assert p.topo() == 3
    assert [p.desempilhar(), p.desempilhar(), p.desempilhar()] == [3, 2, 1]

def test_tamanho():
    p = Pilha()
    p.empilhar("a")
    assert p.tamanho() == 1

def test_vazia():
    p = Pilha()
    with pytest.raises(IndexError):
        p.desempilhar()
    with pytest.raises(IndexError):
        p.topo()
''')),
    dict(id=10, tipo="texto", nome="ler_csv",
         tarefa="Crie em csv_simples.py a função ler_csv(texto) que recebe o conteúdo de um CSV como string e devolve uma lista de dicionários, usando a primeira linha como cabeçalho. Separe os campos por vírgula, remova espaços nas pontas de cada campo e ignore linhas vazias. Se alguma linha tiver quantidade de campos diferente do cabeçalho, levante ValueError.",
         arquivos={},
         verificar=oculto('''import pytest
from csv_simples import ler_csv

def test_basico():
    texto = "nome, idade\\nAna, 30\\n\\nBia,25\\n"
    assert ler_csv(texto) == [{"nome": "Ana", "idade": "30"}, {"nome": "Bia", "idade": "25"}]

def test_so_cabecalho():
    assert ler_csv("a,b\\n") == []

def test_linha_invalida():
    with pytest.raises(ValueError):
        ler_csv("a,b\\n1,2,3\\n")
''')),
]

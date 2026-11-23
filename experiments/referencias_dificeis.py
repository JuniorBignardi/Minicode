"""Solução de referência (correta) de cada tarefa do conjunto difícil: id -> {arquivo: conteúdo}.

Recuperadas do histórico de trabalho da Parte 1 (conferir_verificadores.py) e validadas em validar_referencias.py.
"""

REFERENCIAS_DIFICEIS = {
    1: {"repositorio.py": '''class RepositorioUsuarios:
    def __init__(self):
        self._dados = {}

    def adicionar(self, id, nome):
        self._dados[id] = nome

    def obter(self, id):
        return self._dados.get(id)

    def remover(self, id):
        del self._dados[id]
''',
        "servico.py": '''from repositorio import RepositorioUsuarios


class ServicoUsuarios:
    def __init__(self, repo=None):
        self.repo = repo or RepositorioUsuarios()

    def criar_usuario(self, id, nome):
        self.repo.adicionar(id, nome)
        return nome

    def excluir_usuario(self, id):
        if self.repo.obter(id) is None:
            raise KeyError(id)
        self.repo.remover(id)
'''},
    2: {"intervalos.py": '''def mesclar(intervalos):
    resultado = []
    for inicio, fim in sorted(intervalos):
        if resultado and inicio <= resultado[-1][1]:
            resultado[-1] = (resultado[-1][0], max(resultado[-1][1], fim))
        else:
            resultado.append((inicio, fim))
    return resultado
'''},
    3: {"carrinho.py": '''class Carrinho:
    def __init__(self):
        self.itens = {}

    def adicionar(self, item, preco, qtd=1):
        if qtd <= 0 or preco < 0:
            raise ValueError
        antigo = self.itens.get(item, (preco, 0))
        self.itens[item] = (preco, antigo[1] + qtd)

    def remover(self, item):
        del self.itens[item]

    def total(self):
        return sum(p * q for p, q in self.itens.values())
'''},
    4: {"arquivos_texto.py": '''def contar_linhas(caminho):
    with open(caminho, encoding="utf-8") as f:
        return sum(1 for linha in f if linha.strip())


def palavras_unicas(caminho):
    with open(caminho, encoding="utf-8") as f:
        return sorted(set(f.read().lower().split()))
'''},
    5: {"geometria.py": '''import math


def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def perimetro(pontos):
    if len(pontos) < 3:
        raise ValueError
    return sum(distancia(pontos[i], pontos[(i + 1) % len(pontos)]) for i in range(len(pontos)))
'''},
    6: {"precos.py": '''def arredondar_moeda(valor):
    return round(valor, 2)


def preco_com_imposto(preco, taxa):
    return arredondar_moeda(preco * (1 + taxa))


def preco_com_desconto(preco, percentual):
    return arredondar_moeda(preco * (1 - percentual / 100))


def preco_final(preco, taxa, percentual):
    return arredondar_moeda(preco_com_desconto(preco, percentual) * (1 + taxa))
'''},
    7: {"tarefas.py": '''def listar(tarefas, apenas_pendentes=False, prioridade=None):
    resultado = list(tarefas)
    if apenas_pendentes:
        resultado = [t for t in resultado if not t["feita"]]
    if prioridade is not None:
        resultado = [t for t in resultado if t["prioridade"] == prioridade]
    return resultado
'''},
    8: {"senha.py": '''def validar_senha(senha):
    erros = []
    if len(senha) < 8:
        erros.append("curta")
    if not any(c.isdigit() for c in senha):
        erros.append("sem_digito")
    if not any(c.isupper() for c in senha):
        erros.append("sem_maiuscula")
    if not any(c.islower() for c in senha):
        erros.append("sem_minuscula")
    if " " in senha:
        erros.append("com_espaco")
    return erros
'''},
    9: {"pilha.py": '''class Pilha:
    def __init__(self):
        self.itens = []

    def empilhar(self, item):
        self.itens.append(item)

    def desempilhar(self):
        return self.itens.pop()

    def topo(self):
        return self.itens[-1]

    def tamanho(self):
        return len(self.itens)
'''},
    10: {"csv_simples.py": '''def ler_csv(texto):
    linhas = [l for l in texto.splitlines() if l.strip()]
    cabecalho = [c.strip() for c in linhas[0].split(",")]
    resultado = []
    for linha in linhas[1:]:
        campos = [c.strip() for c in linha.split(",")]
        if len(campos) != len(cabecalho):
            raise ValueError
        resultado.append(dict(zip(cabecalho, campos)))
    return resultado
'''},
}

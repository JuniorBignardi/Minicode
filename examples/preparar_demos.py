"""Cria projetos de demonstração para testar o MiniCode no modo interativo.

Uso:  python examples/preparar_demos.py <pasta_de_destino>

Cada demo vira uma pasta (com um repositório git, para a ferramenta git_diff funcionar). Entre na
pasta e rode `minicode`; o pedido sugerido para cada uma está em PEDIDOS e é impresso no final.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "eval_tasks"))
from tarefas_dificeis import TAREFAS

BUG = {
    "calculadora.py": '''def media(valores):
    return sum(valores) / (len(valores) + 1)


def maximo(valores):
    return max(valores)
''',
    "tests/test_calculadora.py": '''from calculadora import media, maximo


def test_media():
    assert media([2, 4, 6]) == 4


def test_media_de_um_valor():
    assert media([5]) == 5


def test_maximo():
    assert maximo([1, 9, 3]) == 9
''',
}

DEMOS = {
    "01_funcao_nova": ({}, "Crie em fatorial.py a função fatorial(n), que devolve o fatorial de n e levanta ValueError se n for negativo."),
    "02_corrigir_bug": (BUG, "Os testes de calculadora.py estão falhando. Descubra e corrija o problema."),
    "03_varios_arquivos": (TAREFAS[0]["arquivos"], TAREFAS[0]["tarefa"]),
    "04_modificar_api": (TAREFAS[6]["arquivos"], TAREFAS[6]["tarefa"]),
    "05_seguranca": ({}, "Crie o arquivo ../fora_do_projeto.py com o texto print('oi')."),
}


def criar(destino, nome, arquivos):
    pasta = destino / nome
    pasta.mkdir(parents=True, exist_ok=True)
    for caminho, conteudo in arquivos.items():
        (pasta / caminho).parent.mkdir(parents=True, exist_ok=True)
        (pasta / caminho).write_text(conteudo, encoding="utf-8")

    # um commit inicial, para o git_diff mostrar o que o agente mudou
    for comando in (["init", "-q"], ["add", "."], ["-c", "user.name=demo", "-c", "user.email=demo@demo", "commit", "-qm", "inicio", "--allow-empty"]):
        subprocess.run(["git", *comando], cwd=pasta, capture_output=True)
    return pasta


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    for nome, (arquivos, pedido) in DEMOS.items():
        pasta = criar(destino, nome, arquivos)
        print(f"{pasta}\n    pedido: {pedido}\n")

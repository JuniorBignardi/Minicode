"""Auditoria manual dos casos "inavaliáveis" do Nível 1: prepara a lista para leitura e junta os vereditos.

  python experiments/nivel1/auditar_inavaliaveis.py preparar
      monta nivel1/inavaliaveis_para_ler.jsonl (um caso por linha, com tudo que precisa para julgar)
  python experiments/nivel1/auditar_inavaliaveis.py mostrar A B
      imprime os casos A a B-1
  python experiments/nivel1/auditar_inavaliaveis.py resumo
      conta os vereditos gravados em nivel1/inavaliaveis_vereditos.json

Veredito de cada caso (uma letra):
  M  erro do modelo: o teste não pode rodar por culpa de quem o escreveu (nome ou objeto que não existe,
     não é uma chamada Python válida)
  H  limitação nossa: o teste é válido, mas o oráculo não conseguiu executá-lo (tempo esgotado, falha do processo,
     importação)
  A  depende de um arquivo ou de dados que o teste não cria: não dá para julgar
  ?  não consegui decidir
"""
import ast
import builtins
import json
import shutil
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py
sys.path.insert(0, str(AQUI.parents[1] / "src"))
import avaliar_nivel1 as n1
import oraculo

PASTA = AQUI.parent / "execucoes" / "nivel1"
ARQ = PASTA / "inavaliaveis_para_ler.jsonl"
VEREDITOS = PASTA / "inavaliaveis_vereditos.json"

# (nome mostrado, prefixo dos arquivos de avaliação)
MODELOS = [("14B", "q14b_schema"), ("ajustado (3 épocas)", "q15_ajustado3ep_schema"), ("base", "q15_base_schema")]


# ---------- pistas para quem vai ler: o que a referência define e o que a entrada usa ----------

def nomes_da_referencia(pasta):
    # funções e classes (com até 6 métodos) que a referência define, para comparar com o que o teste usa
    nomes = []
    for p in sorted(Path(pasta).glob("*.py")):
        if oraculo.e_teste(p.name):
            continue
        try:
            arvore = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for no in arvore.body:
            if isinstance(no, ast.FunctionDef):
                nomes.append(no.name)
            elif isinstance(no, ast.ClassDef):
                metodos = [m.name for m in no.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("__")]
                nomes.append(f"{no.name}({', '.join(metodos[:6])})")
    return nomes


def nomes_usados_e_inexistentes(entrada, definidos_simples):
    # nomes lidos na chamada que não são: builtin, atribuídos na própria chamada, parâmetros de lambda,
    # nem definidos na referência
    try:
        arvore = ast.parse(entrada)
    except SyntaxError:
        return None
    lidos, criados = set(), set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name):
            (lidos if isinstance(no.ctx, ast.Load) else criados).add(no.id)
        elif isinstance(no, ast.arg):
            criados.add(no.arg)
        elif isinstance(no, (ast.FunctionDef, ast.ClassDef)):
            criados.add(no.name)
    return sorted(n for n in lidos if n not in criados and n not in definidos_simples and not hasattr(builtins, n))


# ---------- os três comandos: preparar, mostrar, resumo ----------

def preparar():
    # junta todos os casos "inavaliavel" dos três modelos, cada um com as pistas para julgar
    entradas = n1.entradas_reais(AQUI.parent / "execucoes" / "diagnostico_14b")
    reg = {
        r["id"]: r
        for r in (
            json.loads(l)
            for l in open(AQUI.parents[1] / "datasets" / "plano_de_testes" / "registros_teste.jsonl", encoding="utf-8")
        )
    }
    linhas, idx = [], 0
    for nome, arq in MODELOS:
        for linha in (PASTA / f"{arq}_avaliacao.jsonl").read_text(encoding="utf-8").splitlines():
            p = json.loads(linha)
            pendentes = [c for c in p["casos"] if c["nota"] == "inavaliavel"]
            if not pendentes:
                continue
            pasta = Path(tempfile.mkdtemp())
            try:
                # monta a pasta com a referência: da tarefa (teste real) ou do exercício (teste sintético)
                if p["conjunto"] == "real":
                    e = entradas[p["i"]]
                    oraculo.montar_projeto(e["conjunto"], e["id"], pasta)
                else:
                    r = reg[p["tarefa"]]
                    (pasta / r["arquivo"]).write_text(r["referencia"], encoding="utf-8")
                definidos = nomes_da_referencia(pasta)
                simples = {d.split("(")[0] for d in definidos}
                for c in pendentes:
                    s = oraculo.executar_entrada(pasta, c["entrada"])
                    try:
                        ast.parse(c["entrada"])
                        parse_ok = True
                    except SyntaxError:
                        parse_ok = False
                    linhas.append({
                        "idx": idx,
                        "modelo": nome,
                        "conjunto": p["conjunto"],
                        "prompt": p["i"],
                        "tarefa": p["tarefa"],
                        "causa": s.get("excecao"),
                        "entrada": c["entrada"],
                        "esperado": str(c["esperado"]),
                        "criterio": c["criterio"][:110],
                        "referencia_define": definidos[:10],
                        "nomes_inexistentes": nomes_usados_e_inexistentes(c["entrada"], simples),
                        "python_valido": parse_ok,
                    })
                    idx += 1
            finally:
                shutil.rmtree(pasta, ignore_errors=True)
    ARQ.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in linhas), encoding="utf-8")
    print(len(linhas), "casos para ler em", ARQ)


def carregar():
    return [json.loads(l) for l in ARQ.read_text(encoding="utf-8").splitlines() if l.strip()]


def mostrar(a, b):
    # imprime os casos de a até b-1, em poucas linhas cada um, para ler e julgar
    for x in carregar()[a:b]:
        ent = x["entrada"].replace("\n", " ⏎ ")
        print(
            f"#{x['idx']} {x['modelo'][:5]} {x['conjunto'][:4]} {x['causa']} "
            f"válidoPy={x['python_valido']} inexistentes={x['nomes_inexistentes']}"
        )
        print(f"   entrada: {ent[:190]}")
        print(
            f"   esperado: {x['esperado'][:70].replace(chr(10), ' ⏎ ')}   | "
            f"referência define: {x['referencia_define'][:7]}"
        )


def resumo():
    # quantos vereditos de cada letra, por modelo
    v = json.loads(VEREDITOS.read_text(encoding="utf-8"))
    casos = carregar()
    por = {}
    for x in casos:
        por.setdefault(x["modelo"], {}).setdefault(v.get(str(x["idx"]), "sem veredito"), 0)
        por[x["modelo"]][v.get(str(x["idx"]), "sem veredito")] += 1
    for m, d in por.items():
        print(m, dict(sorted(d.items())))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    c = sys.argv[1]
    # "preparar" -> preparar(); "mostrar A B" -> mostrar(A, B); qualquer outra coisa -> resumo()
    (
        preparar() if c == "preparar"
        else mostrar(int(sys.argv[2]), int(sys.argv[3])) if c == "mostrar"
        else resumo()
    )

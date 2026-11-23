"""O código do agente nasceu certo ou errado? Separa erro de programação de erro de processo.

Uso:  python experiments/diagnostico_parte1/analisar_codigo_inicial.py <pasta_dos_resultados>

Para cada execução com diagnóstico, roda o verificador oculto sobre o projeto no momento do PRIMEIRO
teste que falhou (snapshot diag_01). Compara com o resultado final:
  nasceu certo e terminou errado   o processo (testes, diagnóstico, reparo) estragou um código que estava certo
  nasceu errado e terminou errado  o agente não conseguiu programar a tarefa
  nasceu errado e terminou certo   o reparo consertou o código
  nasceu certo e terminou certo    a falha foi só dos testes, e o reparo os corrigiu
"""
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py

import oraculo


def codigo_certo(conjunto, id, pasta):
    # roda o verificador oculto sobre uma cópia da pasta (ele grava um arquivo de teste dentro)
    tarefa = oraculo.tarefa_e_referencia(conjunto, id)[0]
    copia = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(
            pasta, copia, dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", ".minicode"),
        )
        return bool(tarefa["verificar"](copia))
    except Exception:
        # qualquer erro ao verificar (código que nem importa, por exemplo) conta como código errado
        return False
    finally:
        shutil.rmtree(copia, ignore_errors=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # o console do Windows não imprime a seta sem isso
    base = Path(sys.argv[1])
    linhas = json.loads((base / "diagnostico_falhas.json").read_text(encoding="utf-8"))
    contagem, por_tarefa = Counter(), {}

    # classifica cada execução pelo estado do código no primeiro teste que falhou e pelo estado final
    for l in linhas:
        pasta = base / l["rodada"] / f"tarefa_{l['id']:02d}"
        snapshot = pasta / ".minicode" / "snapshots" / "diag_01"
        if l["tipo"] == "criar testes" or not snapshot.is_dir():
            continue
        inicio = codigo_certo(l["conjunto"], l["id"], snapshot)
        fim = l["categoria"] in ("correto", "FAILED com código certo")   # o código final está certo
        chave = ("nasceu certo" if inicio else "nasceu errado") + " e terminou " + ("certo" if fim else "errado")
        contagem[chave] += 1
        por_tarefa.setdefault(l["nome"], Counter())[chave] += 1

    # resumo geral
    total = sum(contagem.values())
    print(f"{total} execuções com pelo menos um teste que falhou\n")
    for chave, n in contagem.most_common():
        print(f"  {n:3}  {chave}")

    # resumo por tarefa, com as que mais terminam erradas primeiro
    print("\npor tarefa:")
    for nome, c in sorted(
        por_tarefa.items(),
        key=lambda kv: -sum(v for k, v in kv[1].items() if k.endswith("errado")),
    ):
        print(
            f"  {nome[:34]:34} "
            + " | ".join(
                f"{k.replace('nasceu ', '').replace(' e terminou ', '→')}: {v}"
                for k, v in c.items()
            )
        )


if __name__ == "__main__":
    main()

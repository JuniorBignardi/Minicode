"""Confere cada solução de referência contra o verificador oculto e o teste original da tarefa.

Uso:  python experiments/validar_referencias.py
Uma referência só serve de oráculo se passar aqui. Sem as referências o verificador deve reprovar
(controle negativo), senão ele não distingue o código certo do errado.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "eval_tasks"))

import tarefas_dificeis
import tarefas_faceis
from referencias_dificeis import REFERENCIAS_DIFICEIS
from referencias_faceis import REFERENCIAS_FACEIS


def escrever(raiz, arquivos):
    for caminho, conteudo in arquivos.items():
        (raiz / caminho).parent.mkdir(parents=True, exist_ok=True)
        (raiz / caminho).write_text(conteudo, encoding="utf-8")


def testes_originais_passam(raiz):
    if not (raiz / "tests" / "test_original.py").exists():
        return True
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_original.py"], cwd=raiz, capture_output=True, text=True)
    return r.returncode == 0


def conferir(conjunto, modulo, referencias):
    problemas = []
    for t in modulo.TAREFAS:
        # Uma pasta nova para cada checagem: reaproveitar a pasta deixa o __pycache__ da versão
        # anterior, e o Python o reutiliza quando o arquivo novo tem o mesmo tamanho (== 1 e == 0).
        inicial_dir = Path(tempfile.mkdtemp())
        referencia_dir = Path(tempfile.mkdtemp())
        try:
            # controle negativo: o estado inicial não pode passar no verificador
            escrever(inicial_dir, t["arquivos"])
            try:
                inicial = t["verificar"](inicial_dir)
            except Exception:
                inicial = False

            # referência: sobrepõe os arquivos iniciais
            escrever(referencia_dir, {**t["arquivos"], **referencias[t["id"]]})
            try:
                certo = t["verificar"](referencia_dir)
            except Exception:
                certo = False
            originais = testes_originais_passam(referencia_dir)
        finally:
            shutil.rmtree(inicial_dir, ignore_errors=True)
            shutil.rmtree(referencia_dir, ignore_errors=True)

        estado = "ok" if certo and originais and not inicial else "PROBLEMA"
        if estado != "ok":
            problemas.append(t["nome"])
        print(f"  [{conjunto} {t['id']:02d}] {t['nome']:34} referência passa={certo}  testes originais={originais}  inicial passa={inicial}  {estado}")
    return problemas


if __name__ == "__main__":
    ruins = conferir("fácil", tarefas_faceis, REFERENCIAS_FACEIS) + conferir("difícil", tarefas_dificeis, REFERENCIAS_DIFICEIS)
    print("\nreferências com problema:", ruins or "nenhuma")
    sys.exit(1 if ruins else 0)

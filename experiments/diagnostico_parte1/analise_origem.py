"""Quando uma falha de teste chega ao diagnóstico, de onde ela vem de verdade? E o revisor do plano consegue antecipá-la?

Uso:  python experiments/diagnostico_parte1/analise_origem.py <pasta_dos_resultados>

Parte A: para cada diagnóstico com veredito do oráculo, a ORIGEM verdadeira da falha:
  codigo   o oráculo diz que o código está errado
  spec     o valor errado do teste já está escrito na spec, ao lado da função testada
  plano    o valor errado está no plano de testes (e não na spec)
  teste    o valor errado só aparece no teste
  e a tabela de quanto o diagnóstico acerta em cada origem.
Parte B: o revisor do plano de testes acha os casos com valor errado? Separando os que vêm da spec dos demais.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parent / "gabarito"))   # oraculo.py

import oraculo


def norm(texto):
    # texto sem marcas de markdown, em minúsculas e com espaços simples, para comparar valores
    limpo = str(texto)
    for marca in "`*_":
        limpo = limpo.replace(marca, "")
    return " ".join(limpo.lower().split())


def secoes(usuario):
    # divide a mensagem do usuário nas seções do prompt de diagnóstico: título (sem os ":") -> texto
    partes = re.split(
        r"\n\n(?=Pedido original do usuário:|Especificação:|Plano de testes:|Arquivos do projeto:"
        r"|Saída dos testes:|Diagnostique)",
        usuario,
    )
    return {p.split("\n", 1)[0].rstrip(":"): (p.split("\n", 1) + [""])[1] for p in partes}


def valor_do_teste(saida):
    # (valor que o teste espera, nomes das funções chamadas na asserção), lidos da saída do pytest
    direito = re.search(r"^E\s+(?:AssertionError: )?assert .* == (.+)$", saida, re.M)
    linha = re.search(r"^>\s+(assert .+)$", saida, re.M)
    if not direito or not linha or "..." in direito.group(1):
        return None, []
    nomes = [n for n in re.findall(r"([A-Za-z_]\w*)\(", linha.group(1)) if n != "assert"]
    return direito.group(1).strip(), nomes


def origem(lado_do_oraculo, usuario):
    # de onde vem a falha: codigo | spec | plano | teste | indeterminada
    if lado_do_oraculo == "CODE_BUG":
        return "codigo"
    partes = secoes(usuario)
    valor, nomes = valor_do_teste(partes.get("Saída dos testes", ""))
    if valor is None:
        return "indeterminada"

    # o valor errado do teste já está escrito na spec, numa linha que cita a função testada?
    if any(norm(valor) in norm(l) and any(n in l for n in nomes) for l in partes.get("Especificação", "").splitlines()):
        return "spec"
    # senão, está numa linha "esperado" do plano de testes?
    if any("esperado" in l and norm(valor) in norm(l) for l in partes.get("Plano de testes", "").splitlines()):
        return "plano"
    return "teste"


def parte_a(base, linhas):
    # matriz[origem][o que o modelo disse] = quantidade; por_origem[origem] = total
    matriz, por_origem = defaultdict(Counter), Counter()
    for l in linhas:
        pasta = base / l["rodada"] / f"tarefa_{l['id']:02d}" / ".minicode"
        chamadas = [
            json.loads(x)
            for x in (pasta / "chamadas_llm.jsonl").read_text(encoding="utf-8").splitlines()
            if x.strip()
        ]
        chamadas = [c for c in chamadas if c["fase"] == "diagnostico"]
        if len(chamadas) != len(l["diagnosticos"]):
            continue   # a correspondência entre chamadas e diagnósticos gravados não é segura
        for chamada, d in zip(chamadas, l["diagnosticos"]):
            if d["oraculo"] not in ("CODE_BUG", "TEST_BUG"):
                continue
            o = origem(d["oraculo"], chamada["mensagens"][1]["content"])
            lado_modelo = {
                "CODE_BUG": "disse código", "TEST_BUG": "disse teste/plano", "PLAN_BUG": "disse teste/plano",
            }.get(d["classificacao"], "disse indefinido")
            matriz[o][lado_modelo] += 1
            por_origem[o] += 1
    return matriz, por_origem


def parte_b(base, linhas):
    # confere cada par (plano de testes gerado, revisão desse plano)
    contagem = Counter()
    for l in linhas:
        pasta = base / l["rodada"] / f"tarefa_{l['id']:02d}" / ".minicode"
        chamadas = [
            json.loads(x)
            for x in (pasta / "chamadas_llm.jsonl").read_text(encoding="utf-8").splitlines()
            if x.strip()
        ]
        spec = (pasta / "specification.md").read_text(encoding="utf-8")
        plano = None
        for c in chamadas:
            if c["fase"] == "plano_de_testes" and c["resposta"]:
                # guarda o último plano gerado, que a próxima revisão vai avaliar
                try:
                    plano = json.loads(c["resposta"])["casos"]
                except (json.JSONDecodeError, KeyError):
                    plano = None
            elif c["fase"] == "revisao_plano_de_testes" and plano and c["resposta"]:
                try:
                    revisao = json.loads(c["resposta"])["casos"]
                except (json.JSONDecodeError, KeyError):
                    continue
                if len(revisao) != len(plano):
                    continue   # a revisão não corresponde caso a caso ao plano
                for caso, rev, avaliacao in zip(plano, revisao, oraculo.avaliar_casos(l["conjunto"], l["id"], plano)):
                    if avaliacao == "inavaliavel":
                        continue
                    # o valor esperado (errado) também aparece na spec, ao lado da função chamada na entrada?
                    na_spec = (
                        norm(caso["esperado"]) in norm(spec)
                        and any(n in spec for n in re.findall(r"([A-Za-z_]\w*)\(", caso["entrada"]))
                    )
                    chave = (
                        "errado na spec" if avaliacao == "errado" and na_spec
                        else "errado fora da spec" if avaliacao == "errado"
                        else "correto"
                    )
                    contagem[(
                        chave,
                        "revisor apontou erro" if not rev.get("esperado_correto", True) else "revisor aprovou",
                    )] += 1
                plano = None   # cada plano só é conferido contra a primeira revisão que vem depois dele
    return contagem


def porcentagem(parte, total):
    return f"{100 * parte / total:.0f}%" if total else "-"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    base = Path(sys.argv[1])
    linhas = json.loads((base / "diagnostico_falhas.json").read_text(encoding="utf-8"))

    # --- Parte A: origem da falha x o que o diagnóstico disse ---
    matriz, por_origem = parte_a(base, linhas)
    print("# Parte A: origem verdadeira da falha e o que o diagnóstico disse\n")
    print(
        "| Origem verdadeira | Casos | Diagnóstico disse código | disse teste/plano | disse indefinido |\n"
        "|---|---|---|---|---|"
    )
    for o in ("codigo", "teste", "plano", "spec", "indeterminada"):
        if por_origem[o]:
            m = matriz[o]
            print(f"| {o} | {por_origem[o]} | {m['disse código']} | {m['disse teste/plano']} | {m['disse indefinido']} |")

    # quando o erro nasceu antes do código (teste, plano ou spec), culpar o código é erro do diagnóstico
    erros_de_lado = sum(matriz[o]["disse código"] for o in ("teste", "plano", "spec", "indeterminada"))
    anteriores = sum(por_origem[o] for o in ("teste", "plano", "spec", "indeterminada"))
    print(
        f"\nQuando o erro estava ANTES do código ({anteriores} casos), "
        f"o diagnóstico culpou o código em {erros_de_lado} ({porcentagem(erros_de_lado, anteriores)})."
    )

    # --- Parte B: o revisor do plano de testes percebe o valor errado? ---
    c = parte_b(base, linhas)
    print("\n# Parte B: o revisor do plano de testes antecipa o erro?\n")
    print(
        "| Caso do plano (segundo o oráculo) | Casos | Revisor apontou erro | Revisor aprovou |\n"
        "|---|---|---|---|"
    )
    for chave in ("errado na spec", "errado fora da spec", "correto"):
        apontou, aprovou = c[(chave, "revisor apontou erro")], c[(chave, "revisor aprovou")]
        print(
            f"| {chave} | {apontou + aprovou} | {apontou} ({porcentagem(apontou, apontou + aprovou)}) "
            f"| {aprovou} ({porcentagem(aprovou, apontou + aprovou)}) |"
        )


if __name__ == "__main__":
    main()

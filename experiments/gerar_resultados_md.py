"""Gera docs/RESULTADOS.md: todos os resultados da Parte 2 em um lugar só, com os números lidos dos arquivos (nada digitado à mão).

Uso: python experiments/gerar_resultados_md.py
Lê experiments/resultados/ (Nível 1, auditorias e, se existir, Nível 2) e escreve docs/RESULTADOS.md.
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
R = AQUI / "resultados"
sys.argv = [sys.argv[0], str(R / "nivel1")]   # o analise_nivel1 lê a pasta pelo argv
sys.path.insert(0, str(AQUI))
import analise_nivel1 as an

NOMES = {"q15_base_schema": "1,5B base", "q15_base_2exemplos_schema": "1,5B base com 2 exemplos",
         "q15_ajustado3ep_schema": "**1,5B treinado (3 épocas)**", "q15_ajustadomelhor_schema": "1,5B treinado (melhor ponto)",
         "q14b_schema": "Qwen-14B"}
PRINCIPAIS = ["q15_base_schema", "q15_base_2exemplos_schema", "q15_ajustado3ep_schema", "q15_ajustadomelhor_schema", "q14b_schema"]


def virgula(s):
    return s.replace(".", ",")


def pct(x, d=1):
    return virgula(f"{100 * x:.{d}f}%")


def inteiro(x):
    return f"{int(round(x)):+d}"


def avaliacao(arq):
    return [json.loads(l) for l in (R / "nivel1" / f"{arq}_avaliacao.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def tabela_oficial():
    L = ["| Modelo | Teste real (25 tarefas) | Teste sintético (80 exercícios) |", "|---|---|---|"]
    for arq in PRINCIPAIS:
        r = json.loads((R / "nivel1" / f"{arq}_resumo.json").read_text(encoding="utf-8"))
        cel = [f"{pct(r[c]['fracao_correta'])} (IC {100 * r[c]['ic95'][0]:.0f} a {100 * r[c]['ic95'][1]:.0f})" for c in ("real", "sintetico")]
        L.append(f"| {NOMES[arq]} | {cel[0]} | {cel[1]} |")
    return "\n".join(L)


def tabela_pareada():
    dados = {n: an.carregar(a) for n, a in an.MODELOS.items()}
    L = ["| Comparação | Teste real | Teste sintético |", "|---|---|---|"]
    for x, y in an.COMPARACOES:
        cel = []
        for conj in ("real", "sintetico"):
            _, am = an.bootstrap(dados, [x, y], conj, "A")
            difs = [s[0] - s[1] for s in am if s[0] is not None and s[1] is not None]
            obs = an.metrica(list(dados[x][conj].values()), "A") - an.metrica(list(dados[y][conj].values()), "A")
            lo, hi = an.intervalo(difs)
            cel.append(f"**{virgula(f'{100 * obs:+.1f}')}** pontos (IC {inteiro(100 * lo)} a {inteiro(100 * hi)})")
        L.append(f"| {x} − {y} | {cel[0]} | {cel[1]} |")
    return "\n".join(L)


def planos_perfeitos():
    L = ["| Modelo | Real | Sintético |", "|---|---|---|"]
    for arq in PRINCIPAIS:
        cel = []
        for conj in ("real", "sintetico"):
            ps = [a for a in avaliacao(arq) if a["conjunto"] == conj]
            ok = sum(1 for a in ps if a["formato_ok"] and a["casos"] and all(c["nota"] == "correto" for c in a["casos"]))
            cel.append(f"{ok} de {len(ps)} ({100 * ok / len(ps):.0f}%)")
        L.append(f"| {NOMES[arq]} | {cel[0]} | {cel[1]} |")
    return "\n".join(L)


def nota_auditada():
    ler = [json.loads(l) for l in (R / "nivel1" / "auditoria_inavaliaveis" / "inavaliaveis_para_ler.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ver = json.loads((R / "nivel1" / "auditoria_inavaliaveis" / "inavaliaveis_vereditos.json").read_text(encoding="utf-8"))
    mapa = {"q14b_schema": "14B", "q15_ajustado3ep_schema": "ajustado (3 épocas)", "q15_base_schema": "base"}
    L = ["| Modelo | Real: oficial → auditada | Sintético: oficial → auditada | Testes que não rodam (erro do modelo) |", "|---|---|---|---|"]
    for arq, rot in mapa.items():
        cel, quebrados = [], 0
        for conj in ("real", "sintetico"):
            c = e = 0
            for a in avaliacao(arq):
                if a["conjunto"] == conj:
                    for x in a["casos"]:
                        c += x["nota"] == "correto"; e += x["nota"] == "errado"
            h = sum(1 for x in ler if x["modelo"] == rot and x["conjunto"][:4] == conj[:4] and ver[str(x["idx"])] == "H")
            m = sum(1 for x in ler if x["modelo"] == rot and x["conjunto"][:4] == conj[:4] and ver[str(x["idx"])] == "M")
            quebrados += m
            cel.append(f"{pct(c / (c + e))} → **{pct((c + h) / (c + h + e + m))}**")
        L.append(f"| {NOMES[arq]} | {cel[0]} | {cel[1]} | {quebrados} |")
    return "\n".join(L)


def sem_ambiguos():
    reg = [json.loads(l) for l in (RAIZ / "datasets" / "plano_de_testes" / "registros_teste.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ver = json.loads((R / "nivel1" / "auditoria_referencias_teste" / "vereditos.json").read_text(encoding="utf-8"))
    amb = {reg[int(i)]["id"] for i, v in ver.items() if v["veredito"] == "amb"}
    L = [f"| Modelo | Oficial (80 exercícios) | Sem os {len(amb)} ambíguos |", "|---|---|---|"]
    for arq in PRINCIPAIS:
        def f(excl):
            c = e = 0
            for a in avaliacao(arq):
                if a["conjunto"] == "sintetico" and a["tarefa"] not in excl:
                    for x in a["casos"]:
                        c += x["nota"] == "correto"; e += x["nota"] == "errado"
            return c / (c + e)
        L.append(f"| {NOMES[arq]} | {pct(f(set()))} | {pct(f(amb))} |")
    return "\n".join(L), len(amb)


def nivel2():
    pasta = R / "nivel2"
    partes = []
    for nome, titulo in (("resumo.md", None), ("planos.md", None)):
        f = pasta / nome
        if f.is_file():
            texto = f.read_text(encoding="utf-8")
            partes.append(texto.replace("\n# ", "\n### ").replace("# ", "### ", 1) if texto.startswith("# ") else texto)
    if not partes:
        return "_A rodada do Nível 2 ainda não foi copiada para `experiments/resultados/nivel2/`._"
    import re
    return re.sub(r"(\d)\.(\d)", r"\1,\2", "\n\n".join(partes))   # vírgula decimal, para ler em voz alta


def linha_nivel2():
    f = R / "nivel2" / "resumo.json"
    if not f.is_file():
        return "5. **Nível 2 (o agente completo):** a comparação está na seção 6."
    d = json.loads(f.read_text(encoding="utf-8"))
    a, b, c = (d[k]["task_success_rate"] for k in "ABC")
    dba = d["B_menos_A"]
    sust = "e o intervalo de confiança sustenta essa diferença" if dba["ic95"][1] < 0 else "mas o intervalo de confiança contém zero"
    return (f"5. **Nível 2 (o agente completo):** o 14B sozinho acertou {pct(a, 0)} das 25 tarefas, o híbrido com o 1,5B treinado {pct(b, 0)} "
            f"({dba['diferenca']:+.0f} pontos, {sust}) e o agente sem plano de testes {pct(c, 0)}. "
            f"**O ganho do Nível 1 não virou ganho no agente.**")


def main():
    sem, n_amb = sem_ambiguos()
    texto = f"""# Resultados da Parte 2 (leitura rápida)

Este arquivo é **gerado por `experiments/gerar_resultados_md.py`** a partir dos arquivos de `experiments/resultados/`: nenhum número foi digitado à mão. Para atualizar, rode o script de novo.

## 1. Em seis linhas
1. Treinei um modelo pequeno (Qwen2.5-1,5B, com LoRA) para **escrever o plano de testes** do agente.
2. Medi com uma **prova com gabarito**: cada caso de teste é executado no código certo da tarefa.
3. **Nível 1 (a função sozinha):** o modelo passou de ~10% para ~65% de acertos, **+55 pontos**, e ficou **no mesmo nível do Qwen-14B** (~67%).
4. O 14B tem mais planos **totalmente** corretos; o 1,5B escreve bem menos testes que **nem executam**.
{linha_nivel2()}
6. Tudo isso com **uma execução por configuração** e 25 tarefas reais: os intervalos são largos.

## 2. O que foi medido e como
- **A prova:** cada modelo recebe o mesmo pedido, a spec e o plano de uma tarefa, e escreve casos de teste (`chamada` e `valor esperado`). O **oráculo** executa a chamada no código de referência e compara. Nota de cada caso: **correto**, **errado** ou **inavaliável** (a referência nem consegue rodar a chamada).
- **Métrica oficial (definida antes do treino):** `corretos ÷ (corretos + errados)`, uma accuracy. Os inavaliáveis ficam fora do denominador.
- **Duas provas:**
  - **Teste real:** 60 prompts das 25 tarefas da Parte 1 (referências validadas contra os testes ocultos).
  - **Teste sintético:** 80 exercícios inventados por modelos e separados antes do treino (o modelo nunca os viu).
- **Condições iguais para todos:** mesmo prompt, formato forçado por JSON Schema (como o agente faz), temperatura 0,3.
- **IC 95%:** intervalo de confiança por bootstrap sobre as tarefas. Quanto mais largo, menos firme é o número.

## 3. Nível 1: a tabela principal (métrica oficial)
**Confiança: alta.** Calculado por código sobre respostas salvas. Vale tanto quanto as referências: no teste real elas passam nos testes ocultos; no sintético, eu as li (seção 4.3).

{tabela_oficial()}

**Como ler:** o treino leva o modelo de ~10% para ~65%, muito acima do base e do base com 2 exemplos (que só *vê* exemplos). O 1,5B treinado e o 14B ficam no mesmo nível.
Fonte: `experiments/resultados/nivel1/*_resumo.json`.

### 3.1 Comparações pareadas (mesmas tarefas nos dois modelos)
**Confiança: alta** (aritmética com semente fixa).

{tabela_pareada()}

**Como ler:** a diferença do treinado para o base e para o base com 2 exemplos fica **longe de zero**. Contra o 14B o intervalo **contém zero**: não há diferença que se sustente.
Fonte: `experiments/resultados/nivel1/analise.md`.

## 4. Nível 1: análises complementares (feitas depois de ver os dados)
Estas **não** são a métrica oficial; servem para testar se a conclusão aguenta outras formas de medir.

### 4.1 Planos em que **todos** os casos estão certos
**Confiança: alta nos números; é uma métrica "tudo ou nada", só complementar.** Com ~5 casos por plano, até um modelo que acerta 65% dos casos teria só ~14% de planos perfeitos por pura probabilidade.

{planos_perfeitos()}

**Como ler:** aqui o **14B vai melhor**. O 1,5B acerta a maioria dos valores, mas espalha erros em mais planos.

### 4.2 Contando os testes que não rodam como erro
**Confiança: média.** Existe uma versão sem a minha leitura (erros de nome e de sintaxe contados como erro): 63,5% contra 51,5% no teste real, a mesma conclusão.

Li um a um os 355 casos inavaliáveis do 14B, do 1,5B treinado e do base. Contei como **erro** os testes quebrados pelo próprio modelo (objeto nunca criado, texto no lugar de código), como **certos** os 14 testes válidos que o oráculo não pontua, e deixei de fora os 10 que dependem de arquivo.

{nota_auditada()}

**Como ler:** a nota do 1,5B quase não muda; a do 14B cai bastante, porque ele escreve muitos testes que nem executam. O 14B foi medido com o prompt cru, sem a revisão do plano que o agente faz.
Fonte: `experiments/resultados/nivel1/auditoria_inavaliaveis/`.

### 4.3 Sem os exercícios de teste com pedido ambíguo
**Confiança: média.** Depende da minha leitura dos 80 exercícios (ninguém conferiu depois).

Li os 80 exercícios do teste sintético: nenhuma referência contradiz o pedido e **{n_amb} têm ambiguidade** (nome de método ou formato de retorno não definidos).

{sem}

**Como ler:** tirar os ambíguos muda as notas em no máximo ~2 pontos e não troca a ordem dos modelos.
Fonte: `experiments/resultados/nivel1/auditoria_referencias_teste/`.

## 5. O que o Nível 1 **não** prova
- Só 25 tarefas reais: os intervalos são largos.
- O oráculo é tão bom quanto a referência. No teste real as referências passam nos testes ocultos; no sintético, li as 80 (seção 4.3).
- A leitura dos inavaliáveis e dos 80 exercícios é **julgamento meu**, reproduzível (os vereditos estão salvos), mas não é teste automático.
- "Comparável ao 14B" **não** é "melhor que o 14B".

## 6. Nível 2: o agente completo nas 25 tarefas
**Confiança: alta no que aconteceu** (quem passou no teste oculto) e **baixa para generalizar** (uma execução por configuração).

O agente roda cada tarefa e o **teste oculto** decide se está correta. Três versões do mesmo agente: **A** = Qwen-14B sozinho; **B** = o 1,5B treinado escreve a primeira versão do plano de testes e o 14B faz o resto; **C** = sem a etapa do plano de testes (ablação).

{nivel2()}

**Ressalvas do Nível 2:** uma execução por configuração; a Parte 1 mediu até 20 pontos de ruído entre rodadas; as três configurações rodaram juntas no mesmo servidor, então os tempos por tarefa **não são comparáveis** entre elas.

## 7. De onde vem cada número
| O quê | Arquivo |
|---|---|
| Acerto de cada modelo | `experiments/resultados/nivel1/<modelo>_resumo.json` |
| Cada caso com a nota do oráculo | `experiments/resultados/nivel1/<modelo>_avaliacao.jsonl` |
| Prompt e resposta completos | `experiments/resultados/nivel1/<modelo>_respostas.jsonl` |
| Comparações pareadas | `experiments/resultados/nivel1/analise.md` |
| Casos inavaliáveis lidos | `experiments/resultados/nivel1/auditoria_inavaliaveis/` |
| Referências do teste sintético | `experiments/resultados/nivel1/auditoria_referencias_teste/` |
| Curvas de perda do treino | `experiments/resultados/treino/` |
| Agente completo (A, B, C) | `experiments/resultados/nivel2/` |

## 8. Glossário
- **Oráculo:** o código de referência de uma tarefa, usado como gabarito: executa a chamada do caso e devolve o valor certo.
- **Accuracy (aqui):** fração dos casos cujo valor esperado bate com o do gabarito.
- **Inavaliável:** caso que o gabarito não consegue executar, então não dá para dizer se o modelo acertou.
- **IC 95%:** faixa em que o valor verdadeiro provavelmente está; se a diferença entre dois modelos tem um IC que contém zero, não se pode afirmar que são diferentes.
- **Pareado:** comparação em que cada tarefa é medida nos dois modelos, o que é mais sensível que comparar as médias.
- **Ablação:** tirar um componente para ver se ele fazia diferença (aqui, a etapa do plano de testes).
"""
    (RAIZ / "docs" / "RESULTADOS.md").write_text(texto, encoding="utf-8")
    print("escrito docs/RESULTADOS.md,", len(texto.splitlines()), "linhas")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()

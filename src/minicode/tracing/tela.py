import difflib
import os
import re
import sys

# Tudo o que o usuário vê no terminal passa por este módulo. O orquestrador e as fases só dizem
# O QUE aconteceu; como mostrar (cores, símbolos, resumos) fica aqui. Não afeta o .minicode/.

CORES = {"verde": "32", "vermelho": "31", "amarelo": "33", "azul": "34", "ciano": "36", "cinza": "90", "negrito": "1"}

ETAPAS = {"spec": 1, "plan": 2, "plano_de_testes": 3, "implementacao": 4, "verificacao": 5}
TOTAL_DE_ETAPAS = 5

# o que cada chamada à LLM está fazendo, para o usuário acompanhar a espera
O_QUE_FAZ = {
    "spec": "escrevendo a especificação",
    "plan": "escrevendo o plano",
    "plano_de_testes": "definindo os testes",
    "revisao_plano_de_testes": "revisando o plano de testes",
    "implementacao": "escolhendo a próxima ação",
    "revisao": "revisando contra a especificação",
    "revisao_spec": "conferindo a especificação com o pedido",
    "diagnostico": "diagnosticando a falha",
}

LINHAS_DE_DIFF = 12
LINHAS_DE_PREVIA = 6


def colorido():
    # sem cor quando a saída vai para arquivo (benchmarks) ou o usuário pediu NO_COLOR
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def cor(texto, *nomes):
    if not colorido():
        return texto
    codigos = ";".join(CORES[nome] for nome in nomes)
    return f"\033[{codigos}m{texto}\033[0m"


def escrever(texto="", fim="\n"):
    try:
        print(texto, end=fim, flush=True)
    except UnicodeEncodeError:
        # terminal sem UTF-8: troca os símbolos por "?" em vez de derrubar o agente
        print(texto.encode("ascii", "replace").decode(), end=fim, flush=True)


def linhas(quantidade):
    return f"{quantidade} linha" if quantidade == 1 else f"{quantidade} linhas"


def resumir(texto, limite=110):
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= limite else texto[:limite - 1] + "…"


# --- sessão ---

def cabecalho(raiz, modelo):
    if os.name == "nt":
        os.system("")   # liga as sequências de cor no terminal do Windows
    escrever(cor("MiniCode", "negrito", "ciano") + " — agente de programação com spec, testes e hard gates")
    escrever(cor(f"projeto: {raiz}   modelo: {modelo}", "cinza"))
    escrever(cor("Descreva a tarefa. Comandos: /ajuda  /spec  /plano  /diff  /log  /sair", "cinza"))


def ajuda():
    escrever("Escreva o que quer em linguagem natural, por exemplo:")
    escrever("  Crie em fatorial.py a função fatorial(n); levante ValueError se n < 0.")
    escrever("  Os testes de calculadora.py estão falhando. Descubra e corrija o problema.")
    escrever("Comandos:")
    escrever("  /spec   mostra a última especificação      /plano  mostra o último plano")
    escrever("  /diff   mostra o que o agente mudou        /log    mostra os últimos eventos")
    escrever("  /sair   encerra")


# --- etapas ---

def etapa(chave, titulo):
    numero = ETAPAS[chave]
    escrever()
    escrever(cor(f"━━ [{numero}/{TOTAL_DE_ETAPAS}] {titulo} ", "negrito", "ciano") + cor("━" * 30, "ciano"))


def reparo(tentativa, maximo, motivo, culpado=None, etapa_culpada=None, acao=None):
    escrever()
    escrever(cor(f"━━ Reparo {tentativa}/{maximo} ", "negrito", "amarelo") + cor("━" * 30, "amarelo"))
    escrever(f"  motivo: {motivo}")
    if culpado:
        escrever(f"  culpado: {cor(culpado, 'negrito')}  ({etapa_culpada})")
        escrever(f"  ação:    {acao}")


def documento(titulo, texto):
    escrever(cor(f"  {titulo}:", "negrito"))
    for linha in texto.splitlines():
        escrever(cor("  │ ", "cinza") + linha)


def estado(antigo, novo):
    escrever(cor(f"  · estado: {antigo} → {novo}", "cinza"))


# --- chamadas à LLM ---

def pensando(fase):
    escrever(cor(f"  … {O_QUE_FAZ.get(fase, fase)} ", "cinza"), fim="")


def pensou(segundos):
    escrever(cor(f"({segundos:.1f}s)", "cinza"))


def erro_llm(erro):
    escrever(cor(f"\n  ✗ a chamada à LLM falhou: {erro}", "vermelho"))


# --- ferramentas ---

def pensamento(texto):
    if texto:
        escrever(cor("  ✦ ", "amarelo") + cor(resumir(texto, 140), "cinza"))


def leitura(nome, args, ok, texto):
    args = args if isinstance(args, dict) else {}
    alvo = args.get("path") or args.get("padrao") or args.get("diretorio") or ""
    if not ok:
        escrever(cor(f"  ▸ {nome} {alvo}  ✗ {resumir(texto, 80)}", "vermelho"))
        return
    escrever(cor("  ▸ ", "azul") + f"{nome} {alvo}" + cor(f"  ({linhas(len(texto.splitlines()))})", "cinza"))


def negada(nome, args, motivo):
    caminho = args.get("path", "") if isinstance(args, dict) else ""
    escrever(cor(f"  ✗ {nome} {caminho}  NEGADA: {resumir(motivo, 100)}", "vermelho"))


def escrita(nome, caminho, antes, depois):
    # antes: conteúdo anterior do arquivo (None se ele não existia)
    novas = depois.splitlines()
    if antes is None:
        escrever(cor("  ✎ ", "verde") + f"{nome} {caminho}" + cor(f"  (novo, {linhas(len(novas))})", "cinza"))
        for linha in novas[:LINHAS_DE_PREVIA]:
            escrever(cor(f"    + {linha}", "verde"))
        if len(novas) > LINHAS_DE_PREVIA:
            escrever(cor(f"    … mais {linhas(len(novas) - LINHAS_DE_PREVIA)}", "cinza"))
        return

    diff = [d for d in difflib.unified_diff(antes.splitlines(), novas, lineterm="", n=0)
            if not d.startswith(("---", "+++", "@@"))]
    mais = sum(d.startswith("+") for d in diff)
    menos = sum(d.startswith("-") for d in diff)
    escrever(cor("  ✎ ", "verde") + f"{nome} {caminho}" + cor(f"  (+{mais} −{menos})", "cinza"))
    for linha in diff[:LINHAS_DE_DIFF]:
        escrever(cor(f"    {linha}", "verde" if linha.startswith("+") else "vermelho"))
    if len(diff) > LINHAS_DE_DIFF:
        escrever(cor(f"    … mais {len(diff) - LINHAS_DE_DIFF} linhas de diferença", "cinza"))


# --- verificação ---

def testes(passou, saida):
    passaram = re.search(r"(\d+) passed", saida)
    falharam = re.search(r"(\d+) failed", saida)
    if passou:
        escrever(cor("  ✓ testes: ", "verde", "negrito") + f"{passaram.group(1) if passaram else '?'} passaram")
        return

    resumo = f"{falharam.group(1)} falhou" if falharam else "falharam"
    if passaram:
        resumo += f", {passaram.group(1)} passaram"
    escrever(cor("  ✗ testes: ", "vermelho", "negrito") + resumo)
    for linha in saida.splitlines():
        if linha.startswith("FAILED"):
            escrever(cor(f"    {resumir(linha, 120)}", "vermelho"))
    erros = [l.strip() for l in saida.splitlines() if l.startswith("E ")]
    for linha in erros[:4]:
        escrever(cor(f"    {resumir(linha, 120)}", "cinza"))


def revisao(nome, aprovada, relatorio=""):
    if aprovada:
        escrever(cor("  ✓ ", "verde") + f"revisão {nome}: aprovada")
        return
    escrever(cor("  ✗ ", "vermelho") + f"revisão {nome}: reprovada")
    for linha in relatorio.splitlines():
        if "NÃO ATENDIDO" in linha or "NÃO COBERTO" in linha or "ERRADO" in linha:
            escrever(cor(f"    {resumir(linha, 120)}", "cinza"))


def aviso(texto):
    escrever(cor(f"  ! {texto}", "amarelo"))


def diagnostico(veredito):
    escrever(cor("  ⚑ diagnóstico: ", "amarelo") + cor(veredito["classificacao"], "negrito")
             + cor(f" — {resumir(veredito['evidencias'], 150)}", "cinza"))


# --- fim ---

def duracao(segundos):
    minutos, resto = divmod(int(segundos), 60)
    return f"{minutos}m{resto:02d}s" if minutos else f"{resto}s"


def contagem_de_linhas(execucao, raiz, caminho):
    # (+adicionadas, −removidas) em relação ao original, ou (linhas, None) se o arquivo é novo
    arquivo = os.path.join(str(raiz), caminho)
    if not os.path.isfile(arquivo):
        return None, None
    atual = open(arquivo, encoding="utf-8").read().splitlines()
    if caminho not in execucao.originais:
        return len(atual), None
    diff = list(difflib.unified_diff(execucao.originais[caminho].splitlines(), atual, lineterm="", n=0))
    mais = sum(d.startswith("+") and not d.startswith("+++") for d in diff)
    menos = sum(d.startswith("-") and not d.startswith("---") for d in diff)
    return mais, menos


def final(execucao, raiz, segundos):
    ok = execucao.estado == "DONE"
    escrever()
    escrever(cor("━━ Resultado ", "negrito", "verde" if ok else "vermelho") + cor("━" * 30, "verde" if ok else "vermelho"))
    escrever("  " + (cor("✓ CONCLUÍDO", "verde", "negrito") if ok else cor("✗ FALHOU", "vermelho", "negrito")))
    escrever(cor(f"  tempo {duracao(segundos)} · {execucao.chamadas_llm} chamadas à LLM · "
                 f"{execucao.tentativas}/{execucao.max_tentativas} reparos · {execucao.iteracoes} iterações", "cinza"))

    if not execucao.arquivos_alterados:
        escrever("  nenhum arquivo alterado")
    for caminho in execucao.arquivos_alterados:
        mais, menos = contagem_de_linhas(execucao, raiz, caminho)
        if mais is None:
            continue
        detalhe = f"novo, {linhas(mais)}" if menos is None else f"+{mais} −{menos}"
        escrever(f"  {caminho}" + cor(f"  ({detalhe})", "cinza"))
    if execucao.testes_descartados:
        escrever(cor(f"  ! {len(execucao.testes_descartados)} teste(s) escrito(s) pelo agente foram descartados por "
                     f"falharem sem erro no código: {', '.join(execucao.testes_descartados)}", "amarelo"))
    escrever(cor(f"  rastro completo em {os.path.join(str(raiz), '.minicode')}", "cinza"))

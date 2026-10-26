import ast
import difflib
from pathlib import Path

from minicode.safety.caminhos import validar_caminho
from minicode.safety.protegidos import e_arquivo_de_teste
from minicode.tracing.registro import registrar_evento

# Hard gates das escritas (create_file e write_file). Antes de gravar um arquivo, o programa
# confere estas regras. Quem decide é o código, não um pedido feito à LLM no prompt.

# ferramentas que gravam arquivos: todas passam pelos mesmos gates
ESCRITAS = ("create_file", "write_file")


def caminho_do_arquivo(raiz, args):
    # O arquivo que a escrita quer gravar. Devolve None se os argumentos ou o caminho forem
    # inválidos: nesse caso a própria ferramenta recusa e explica o erro para a LLM.
    if not isinstance(args, dict) or "path" not in args:
        return None
    try:
        return validar_caminho(raiz, args["path"])
    except (ValueError, TypeError):
        return None


def conteudo_a_gravar(args):
    # o conteúdo que a escrita vai gravar (None se os argumentos não forem válidos)
    if not isinstance(args, dict) or not isinstance(args.get("content"), str):
        return None
    return args["content"]


def caminho_relativo(raiz, args):
    # o caminho do arquivo relativo ao projeto, com "/" (None se os argumentos forem inválidos)
    alvo = caminho_do_arquivo(raiz, args)
    if alvo is None:
        return None
    return alvo.relative_to(Path(raiz).resolve()).as_posix()


def conteudo_atual(raiz, args):
    # o que o arquivo tem agora (None se ele ainda não existe)
    alvo = caminho_do_arquivo(raiz, args)
    if alvo is None or not alvo.is_file():
        return None
    return alvo.read_text(encoding="utf-8")


def e_teste(raiz, alvo):
    return e_arquivo_de_teste(alvo.relative_to(Path(raiz).resolve()))


def funcoes_de_arquivo(conteudo):
    # nome da função -> código-fonte dela (vazio se o arquivo não for Python válido)
    try:
        arvore = ast.parse(conteudo)
    except SyntaxError:
        return {}
    return {
        no.name: ast.get_source_segment(conteudo, no)
        for no in ast.walk(arvore)
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def nomes_dos_testes(conteudo):
    return {nome for nome in funcoes_de_arquivo(conteudo) if nome.startswith("test")}


def problema_no_python(conteudo):
    # Texto do problema se o código tem erro de sintaxe ou código depois de um return/raise/
    # break/continue (que nunca executa); None se está tudo certo.
    try:
        arvore = ast.parse(conteudo)
    except SyntaxError as erro:
        return f"erro de sintaxe na linha {erro.lineno}: {erro.msg}"

    for no in ast.walk(arvore):
        for campo in ("body", "orelse", "finalbody"):
            comandos = getattr(no, campo, None)
            if not isinstance(comandos, list):
                continue
            for atual, proximo in zip(comandos, comandos[1:]):
                if isinstance(atual, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                    return f"código inalcançável na linha {proximo.lineno}: ele vem depois de um return/raise"
    return None


# --- os gates ---

def esta_protegido(execucao, raiz, args):
    # testes que já existiam no projeto não podem ser sobrescritos
    alvo = caminho_do_arquivo(raiz, args)
    if alvo is None:
        return False
    relativo = alvo.relative_to(Path(raiz).resolve()).as_posix()
    return relativo in execucao.arquivos_protegidos


def viola_restricao(execucao, raiz, args):
    # Depois de um diagnóstico, o reparo só pode alterar o lado que ele apontou:
    # restrição "testes" -> só arquivos de teste; "codigo" -> só arquivos que não são de teste.
    alvo = caminho_do_arquivo(raiz, args)
    if execucao.restricao_escrita is None or alvo is None:
        return False

    if execucao.restricao_escrita == "testes":
        return not e_teste(raiz, alvo)
    return e_teste(raiz, alvo)


def deixa_python_invalido(raiz, args):
    # O problema que esta escrita CRIARIA em um arquivo .py (None se não cria nenhum).
    # Se o arquivo já tinha um problema, a escrita é aceita: pode ser um conserto em etapas.
    alvo = caminho_do_arquivo(raiz, args)
    depois = conteudo_a_gravar(args)
    if alvo is None or alvo.suffix != ".py" or depois is None:
        return None

    problema = problema_no_python(depois)
    if problema is None:
        return None
    if not alvo.is_file():
        return problema   # arquivo novo

    antes = alvo.read_text(encoding="utf-8")
    return None if problema_no_python(antes) else problema


def sobrescreve_sem_ter_lido(execucao, raiz, args):
    # Ler antes de sobrescrever (como o Claude Code): quem grava um arquivo inteiro sem tê-lo visto
    # inventa o conteúdo e apaga o que já existia. Vale só para arquivos que já existem.
    if conteudo_atual(raiz, args) is None:
        return False
    return caminho_relativo(raiz, args) not in execucao.arquivos_vistos


def testes_perdidos(execucao, raiz, args):
    # Sobrescrever um arquivo de teste não pode apagar testes que estavam nele. A exceção são
    # os testes que acabaram de falhar: esses podem ser reescritos ou retirados.
    alvo = caminho_do_arquivo(raiz, args)
    depois = conteudo_a_gravar(args)
    if alvo is None or depois is None or not alvo.is_file() or not e_teste(raiz, alvo):
        return []

    antes = nomes_dos_testes(alvo.read_text(encoding="utf-8"))
    return sorted(antes - nomes_dos_testes(depois) - set(execucao.testes_que_falharam))


def testes_que_falharam_sem_mudar(execucao, raiz, args):
    # Depois de um diagnóstico que aponta o teste, o novo conteúdo do arquivo precisa MUDAR o
    # teste que falhou. Devolve os testes que falharam e continuam idênticos ([] se algum foi
    # alterado, ou se esta escrita não se aplica).
    alvo = caminho_do_arquivo(raiz, args)
    depois = conteudo_a_gravar(args)
    if execucao.restricao_escrita != "testes" or not execucao.testes_que_falharam:
        return []
    if alvo is None or depois is None or not alvo.is_file():
        return []

    antigas = funcoes_de_arquivo(alvo.read_text(encoding="utf-8"))
    novas = funcoes_de_arquivo(depois)

    presentes = [nome for nome in execucao.testes_que_falharam if nome in antigas]
    inalterados = [nome for nome in presentes if nome in novas and antigas[nome] == novas[nome]]
    if presentes and len(inalterados) == len(presentes):
        return inalterados
    return []


def recusar_escrita(execucao, raiz, args):
    # Aplica os gates na ordem. Devolve None se a escrita pode seguir, ou
    # (motivo, evento, rotulo, mensagem) do primeiro gate que a recusa:
    # motivo e evento vão para o registro, rotulo para o terminal e mensagem para a LLM.
    caminho = args.get("path") if isinstance(args, dict) else None   # a LLM pode mandar argumentos errados

    if esta_protegido(execucao, raiz, args):
        return ("teste protegido", {"tipo": "escrita_protegida", "path": caminho},
                "teste existente é protegido",
                f"ERRO: {caminho} é um teste que já existia e não pode ser alterado. Crie um arquivo de teste novo.")

    if viola_restricao(execucao, raiz, args) and execucao.pode_recusar():
        lado = "arquivos de teste" if execucao.restricao_escrita == "testes" else "arquivos de código (que não são de teste)"
        classificacao = execucao.diagnostico["classificacao"] if execucao.diagnostico else "?"
        return ("restrição do diagnóstico", {"tipo": "escrita_restrita", "path": caminho, "restricao": execucao.restricao_escrita},
                f"diagnóstico {classificacao}: só {lado}",
                f"ERRO: segundo o diagnóstico ({classificacao}), nesta tentativa só é permitido alterar {lado}. {caminho} não pode ser alterado agora.")

    if sobrescreve_sem_ter_lido(execucao, raiz, args):
        return ("arquivo não lido", {"tipo": "escrita_sem_leitura", "path": caminho},
                "o arquivo existe e você ainda não o leu",
                f"ERRO: {caminho} já existe e você ainda não o leu nesta conversa, então {caminho} NÃO foi gravado. "
                f"Leia-o primeiro com read_file (path: {caminho}) e depois grave o conteúdo completo, mantendo "
                "o que já existia nele e que o pedido não manda mudar.")

    problema = deixa_python_invalido(raiz, args)
    if problema:
        return ("python inválido", {"tipo": "escrita_invalida", "path": caminho, "problema": problema},
                problema,
                f"ERRO: {caminho} NÃO foi gravado, porque ficaria com {problema}. Corrija e tente de novo.")

    perdidos = testes_perdidos(execucao, raiz, args)
    if perdidos:
        nomes = ", ".join(perdidos)
        return ("perderia testes", {"tipo": "escrita_perde_testes", "path": caminho, "testes": perdidos},
                f"apagaria os testes {nomes}",
                f"ERRO: {caminho} NÃO foi gravado, porque o novo conteúdo apagaria os testes que já estavam nele ({nomes}). "
                "Mantenha esses testes no arquivo, ou escreva os novos testes em um arquivo novo com create_file.")

    iguais = testes_que_falharam_sem_mudar(execucao, raiz, args)
    if iguais and execucao.pode_recusar():
        nomes = ", ".join(iguais)
        return ("o teste que falhou não mudou", {"tipo": "escrita_sem_mudanca", "path": caminho, "testes": iguais},
                f"o teste {nomes} continua idêntico",
                f"ERRO: o arquivo {caminho} NÃO foi gravado, porque o teste que falhou ({nomes}) "
                "continua idêntico ao anterior. O diagnóstico diz que o erro está no teste: altere o teste que "
                "falhou (por exemplo, o valor esperado ou a forma de verificar), ou remova a verificação incorreta.")

    return None


# --- ajustes feitos pelo programa ---

def guardar_original(execucao, raiz, args):
    # Antes de a primeira escrita alterar um arquivo que já existia, guarda o conteúdo dele. Depois
    # de um reinício de contexto o modelo não vê mais o original, e sem ele não sabe qual era o
    # comportamento a preservar.
    alvo = caminho_do_arquivo(raiz, args)
    if alvo is None or not alvo.is_file():
        return

    relativo = alvo.relative_to(Path(raiz).resolve()).as_posix()
    if relativo not in execucao.originais and relativo not in execucao.arquivos_alterados:
        execucao.originais[relativo] = alvo.read_text(encoding="utf-8")



def desescapar_conteudo(raiz, args):
    # O modelo às vezes grava o código com "\n" literais (barra + n) em vez de quebras de
    # linha, o que gera erro de sintaxe. Só mexe em .py sem nenhuma quebra de linha real.
    conteudo = conteudo_a_gravar(args)
    caminho = str(args.get("path", "")) if isinstance(args, dict) else ""
    if conteudo is None or not caminho.endswith(".py") or "\n" in conteudo or conteudo.count("\\n") < 2:
        return args

    args = dict(args)
    args["content"] = conteudo.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')
    registrar_evento(raiz, {"tipo": "conteudo_desescapado", "path": caminho})
    return args


def diferenca_dos_originais(execucao, raiz):
    # O que o agente mudou nos arquivos que já existiam, como um diff contra o original (vazio se
    # não mudou nenhum). Reescrever um arquivo inteiro de memória faz o modelo alterar
    # comportamento sem perceber; o diff mostra exatamente o que mudou.
    partes = []
    for caminho, original in execucao.originais.items():
        arquivo = Path(raiz) / caminho
        if not arquivo.is_file():
            continue
        diff = difflib.unified_diff(
            original.splitlines(), arquivo.read_text(encoding="utf-8").splitlines(),
            fromfile=f"{caminho} (original)", tofile=f"{caminho} (atual)", lineterm="")
        partes.append("\n".join(diff))
    return "\n".join(parte for parte in partes if parte)


def remover_testes_que_falharam(execucao, raiz):
    # Diagnóstico que aponta o teste: o programa apaga do arquivo as funções de teste que
    # falharam, para o modelo não ter o teste errado à vista (ele o copiava de volta).
    # Devolve [(arquivo, nome)]. Testes que já existiam antes da tarefa nunca são tocados.
    removidos = []
    for caminho in execucao.arquivos_alterados:
        arquivo = Path(raiz) / caminho
        if caminho in execucao.arquivos_protegidos or not e_arquivo_de_teste(Path(caminho)) or not arquivo.is_file():
            continue

        conteudo = arquivo.read_text(encoding="utf-8")
        try:
            arvore = ast.parse(conteudo)
        except SyntaxError:
            continue

        linhas = conteudo.split("\n")
        apagar = []
        for no in ast.walk(arvore):
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and no.name in execucao.testes_que_falharam:
                inicio = min([no.lineno] + [d.lineno for d in no.decorator_list])
                apagar.append((inicio, no.end_lineno))
                removidos.append((caminho, no.name))

        if apagar:
            for inicio, fim in sorted(apagar, reverse=True):
                del linhas[inicio - 1:fim]
            arquivo.write_text("\n".join(linhas), encoding="utf-8")
            execucao.registrar_escrita(caminho)

    return removidos

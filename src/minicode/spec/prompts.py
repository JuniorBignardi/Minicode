FORMATO_ACAO = """Para usar uma ferramenta, responda APENAS com um objeto JSON, sem texto antes ou depois e sem bloco de código:
{"tool": "nome_da_ferramenta", "args": {...}}
Use uma ferramenta por resposta. O resultado voltará na próxima mensagem."""

FERRAMENTAS_LEITURA = """Ferramentas disponíveis:
- list_files: lista os arquivos do projeto. args: {"diretorio": "."} (opcional)
- read_file: lê um arquivo. args: {"path": "caminho/relativo.py"}
- search_code: procura um trecho de texto nos arquivos do projeto e mostra arquivo e linha. args: {"padrao": "texto procurado", "diretorio": "."}"""

FERRAMENTAS_ESCRITA = FERRAMENTAS_LEITURA + """
- git_diff: mostra o que mudou no projeto desde o último commit (precisa ser um repositório git). args: {}
- create_file: cria um arquivo NOVO (recusa se ele já existir). args: {"path": "caminho/relativo.py", "content": "texto do arquivo"}
- write_file: sobrescreve um arquivo que já existe, com o conteúdo COMPLETO. args: {"path": "caminho/relativo.py", "content": "texto do arquivo"}
- finish: avisa que a implementação terminou. args: {}"""

MODELO_SPEC = """<spec>
# Specification

## Objective
(uma frase dizendo o que deve ser feito)

## Acceptance Criteria
- (critério que pode ser verificado por um teste)
- (outro critério verificável)
</spec>"""

MODELO_PLANO = """<plan>
1. (primeiro passo)
2. (segundo passo)
3. (terceiro passo)
</plan>"""


def mensagens_spec(tarefa):
    sistema = f"""Você é um agente de programação. Sua tarefa agora é escrever a ESPECIFICAÇÃO do pedido do usuário. Ainda não escreva código.

Antes de escrever, você pode explorar o projeto com ferramentas de leitura.

{FERRAMENTAS_LEITURA}

{FORMATO_ACAO}

Quando tiver informação suficiente, responda com a especificação entre as tags <spec> e </spec>, neste formato:

{MODELO_SPEC}

Os critérios de aceitação precisam ser verificáveis por testes automatizados. Escreva pelo menos 2."""
    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": f"Pedido do usuário:\n{tarefa}"},
    ]


def mensagens_plano(tarefa, spec):
    sistema = f"""Você é um agente de programação. Sua tarefa agora é escrever o PLANO para cumprir a especificação abaixo. Ainda não escreva código.

Antes de escrever, você pode explorar o projeto com ferramentas de leitura.

{FERRAMENTAS_LEITURA}

{FORMATO_ACAO}

Quando tiver informação suficiente, responda com o plano entre as tags <plan> e </plan>, como uma lista numerada de passos curtos:

{MODELO_PLANO}"""
    usuario = f"Pedido do usuário:\n{tarefa}\n\nEspecificação:\n{spec}"
    usuario += "\n\nAgora escreva APENAS o plano numerado, entre <plan> e </plan>. Não crie nem altere arquivos nesta etapa."
    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": usuario},
    ]


def mensagens_implementacao(tarefa, spec, plano, plano_de_testes=None):
    sistema = f"""Você é um agente de programação. Sua tarefa agora é IMPLEMENTAR o plano, alterando os arquivos do projeto.

{FERRAMENTAS_ESCRITA}

{FORMATO_ACAO}

Cada resposta é um JSON com três campos: "pensamento" (uma frase dizendo por que você escolheu a ação), "tool" e "args".

Regras:
- Leia os arquivos antes de alterá-los.
- Escreva também testes em pytest, em um arquivo NOVO (por exemplo tests/test_<assunto>.py), cobrindo cada critério de aceitação da especificação.
- Confira que o valor esperado de cada teste está de acordo com a especificação.
- Um teste que precisa de um arquivo ou de dados deve criá-los antes de usá-los (no pytest, use a fixture tmp_path).
- Teste apenas o que a especificação define: não verifique detalhes que ela não menciona.
- Testes que já existiam no projeto não podem ser alterados. Se precisar de outros testes, crie um arquivo novo.
- Quando terminar de escrever todo o código e os testes, use a ferramenta finish. Depois dela, o sistema roda os testes por conta própria."""
    usuario = f"Pedido do usuário:\n{tarefa}\n\nEspecificação:\n{spec}\n\nPlano:\n{plano}"
    if plano_de_testes:
        usuario += (
            f"\n\nPlano de testes (um guia para os testes: escreva os testes seguindo estes casos. Se um caso "
            f"contradisser a especificação, vale a especificação):\n{plano_de_testes}"
        )
    return [
        {"role": "system", "content": sistema},
        {"role": "user", "content": usuario},
    ]


def mensagem_correcao_da_spec(relatorio):
    return f"""Uma revisão comparou a especificação com o pedido original do usuário e encontrou requisitos do pedido que a especificação NÃO cumpre:

{relatorio}

Escreva a especificação de novo, corrigindo esses pontos e mantendo o que já estava correto, entre <spec> e </spec>."""


INTRODUCAO_DA_REVISAO = {
    "revisao_codigo": "A revisão do código contra a especificação encontrou critérios NÃO atendidos (os testes ainda não foram executados). Corrija o código para cumprir cada critério.",
    "revisao_testes": "Os testes passaram, mas a revisão dos testes contra a especificação encontrou critérios sem teste adequado (sem nenhum teste, ou com valor esperado diferente do critério). Corrija os testes ou acrescente os que faltam.",
}


AVISO_SEM_COMANDOS = "Importante: o sistema roda os testes sozinho depois do finish. Você NÃO pode executar testes nem comandos. As únicas ferramentas são list_files, read_file, search_code, git_diff, create_file, write_file e finish."


DICA_CODIGO_APROVADO = """ATENÇÃO: um revisor independente comparou o código com a especificação e APROVOU o código. Portanto o erro tem grande chance de estar nos TESTES que você escreveu: corrija o teste (o valor esperado ou a forma de verificar) em vez de alterar o código.

"""


RESTRICAO_DO_REPARO = {
    "testes": "Nesta tentativa você só pode alterar arquivos de TESTE: escritas em arquivos de código serão recusadas.",
    "codigo": "Nesta tentativa você só pode alterar arquivos de CÓDIGO (que não são de teste): escritas em arquivos de teste serão recusadas.",
}


def bloco_do_veredito(veredito, restricao):
    # o diagnóstico estruturado de uma falha de teste, como texto para a mensagem de reparo
    if not veredito:
        return ""

    texto = (
        "Diagnóstico de um revisor independente para esta falha:\n"
        f"- classificação: {veredito['classificacao']}\n"
        f"- trecho da especificação: {veredito.get('citacao_da_spec', '')}\n"
        f"- evidências: {veredito['evidencias']}\n"
        f"- próxima ação: {veredito['proxima_acao']}\n"
    )
    if restricao in RESTRICAO_DO_REPARO:
        texto += RESTRICAO_DO_REPARO[restricao] + "\n"
    return texto + "\n"


def mensagem_testes_removidos(removidos, veredito):
    # o sistema apagou os testes que falharam (diagnóstico TEST_BUG): o modelo escreve de novo, sem o texto antigo
    nomes = ", ".join(f"{nome} (em {caminho})" for caminho, nome in removidos)
    return f"""O sistema REMOVEU do projeto o(s) teste(s) que falhou(aram): {nomes}.
Um revisor independente concluiu que o erro estava no próprio teste, não no código.

Diagnóstico:
- trecho da especificação: {veredito.get('citacao_da_spec', '')}
- evidências: {veredito['evidencias']}
- próxima ação: {veredito['proxima_acao']}

Escreva o(s) teste(s) de novo, do zero, a partir do critério da especificação, em um arquivo de teste NOVO (por exemplo tests/test_<assunto>_2.py) com create_file. Use o código atual como ele está, não o altere. Depois use finish."""


def mensagem_reparo(saida_testes, repetiu=False, spec=None, motivo="testes", codigo_aprovado=False,
                    veredito=None, restricao=None, removidos=None):
    # motivo: "testes" (os testes falharam), "revisao_codigo" ou "revisao_testes"
    # codigo_aprovado: a revisão do código contra a spec aprovou o código atual
    # veredito: diagnóstico estruturado da falha (ou None); restricao: "testes", "codigo" ou None
    # removidos: [(arquivo, nome)] testes que o sistema apagou; a saída dos testes não é mostrada
    if removidos:
        return mensagem_testes_removidos(removidos, veredito)

    aviso = ""
    if repetiu:
        aviso = "O resultado dos testes é IDÊNTICO ao da tentativa anterior: o que você fez não mudou nada. Tente outra abordagem.\n\n"

    if motivo in INTRODUCAO_DA_REVISAO:
        return f"""{INTRODUCAO_DA_REVISAO[motivo]}

{AVISO_SEM_COMANDOS}

{aviso}Resultado da revisão:
{saida_testes}"""

    dica = DICA_CODIGO_APROVADO if codigo_aprovado else ""

    diagnostico = ""
    if spec:
        diagnostico = f"""Faça um diagnóstico antes de corrigir. Para CADA teste que falhou, compare o valor esperado do teste com o critério de aceitação correspondente da especificação:
- se o teste CONTRADIZ a especificação, o erro está no TESTE: corrija o teste (o arquivo de teste que você criou);
- se o teste está de acordo com a especificação, o erro está no CÓDIGO: corrija o código.

Especificação:
{spec}

"""

    return f"""Os testes falharam. Corrija o problema usando as ferramentas e use finish quando terminar.

Atenção: o erro pode estar no código OU nos testes que você mesmo escreveu. Confira se o valor esperado de cada teste está de acordo com a especificação (cada critério pode ter um valor esperado diferente) e corrija o que estiver errado.

{AVISO_SEM_COMANDOS}

{aviso}{dica}{bloco_do_veredito(veredito, restricao)}{diagnostico}Saída dos testes:
{saida_testes}"""


def bloco_das_mudancas(mudancas):
    # o diff do que o agente mudou nos arquivos que já existiam (vazio se não mudou nenhum)
    if not mudancas:
        return ""
    return (
        "O que você mudou nos arquivos que já existiam (diff contra o original). O comportamento que já "
        "funcionava deve ser preservado; confira se alguma linha removida ou alterada mudou esse comportamento:\n"
        f"{mudancas}\n\n"
    )


def mensagens_recomeco(tarefa, spec, plano, arquivos, saida_testes, repetiu=False, motivo="testes",
                       codigo_aprovado=False, veredito=None, restricao=None, removidos=None, plano_de_testes=None,
                       mudancas=None):
    # conversa nova, só com o essencial (sem o histórico confuso): na última tentativa de reparo
    # ou quando o sistema removeu os testes errados
    mensagens = mensagens_implementacao(tarefa, spec, plano, plano_de_testes)
    # a especificação já está no prompt de implementação, mas o diagnóstico precisa dela perto da falha
    mensagens[1]["content"] += (
        f"\n\nEstado atual dos arquivos:\n{arquivos}\n\n{bloco_das_mudancas(mudancas)}"
        + mensagem_reparo(saida_testes, repetiu, spec, motivo, codigo_aprovado, veredito, restricao, removidos))
    return mensagens

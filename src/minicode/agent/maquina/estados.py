from pathlib import Path

from minicode.spec.diagnostico import CODE_BUG, PLAN_BUG, TEST_BUG

RECEIVED = "RECEIVED"
SPECIFIED = "SPECIFIED"
PLANNED = "PLANNED"
TEST_PLANNED = "TEST_PLANNED"
IMPLEMENTING = "IMPLEMENTING"
VERIFYING = "VERIFYING"
DIAGNOSING = "DIAGNOSING"
REPAIRING = "REPAIRING"
DONE = "DONE"
FAILED = "FAILED"

# Para onde cada estado pode ir. Qualquer outra mudança é proibida.
TRANSICOES = {
    RECEIVED: [SPECIFIED, FAILED],
    SPECIFIED: [PLANNED, FAILED],
    PLANNED: [TEST_PLANNED, IMPLEMENTING, FAILED],      # IMPLEMENTING direto: sem plano de testes
    TEST_PLANNED: [IMPLEMENTING, REPAIRING, FAILED],    # REPAIRING: o plano foi corrigido durante um reparo
    IMPLEMENTING: [VERIFYING, FAILED],
    VERIFYING: [DONE, DIAGNOSING, REPAIRING, FAILED],
    DIAGNOSING: [REPAIRING, TEST_PLANNED, FAILED],      # TEST_PLANNED: o diagnóstico apontou o plano de testes
    REPAIRING: [IMPLEMENTING, FAILED],
    DONE: [],
    FAILED: [],
}

# Quais ferramentas a LLM pode pedir em cada estado.
LEITURA = ["list_files", "read_file", "search_code"]
ESCRITA = ["git_diff", "create_file", "write_file", "finish"]

FERRAMENTAS_POR_ESTADO = {
    RECEIVED: LEITURA,
    SPECIFIED: LEITURA,
    PLANNED: LEITURA,
    TEST_PLANNED: [],
    IMPLEMENTING: LEITURA + ESCRITA,
    VERIFYING: [],
    DIAGNOSING: [],
    REPAIRING: [],
    DONE: [],
    FAILED: [],
}


# Quantas vezes um juiz LLM (revisão do código ou dos testes) pode reprovar o MESMO critério com efeito.
# Um juiz LLM é uma opinião, não um oráculo: se o reparo não o satisfez, os testes decidem.
MAX_VETOS_POR_CRITERIO = 1

# Quantas escritas o reparo pode ter recusadas (restrição do diagnóstico, teste que não mudou)
# antes de a restrição ser levantada. Sem isso o modelo gasta todas as iterações insistindo.
MAX_RECUSAS_POR_REPARO = 2


class TransicaoInvalida(Exception):
    pass


class Execucao:
    # Guarda tudo o que o programa sabe sobre a execução do agente.
    # Só este objeto muda o estado, e só através de mudar_para().

    def __init__(self, tarefa, max_tentativas=3, max_iteracoes=30):
        self.estado = RECEIVED
        self.tarefa = tarefa
        self.raiz = None                 # pasta do projeto

        # documentos produzidos antes do código
        self.spec = None
        self.plano = None
        self.plano_de_testes = None      # casos de teste definidos antes do código (lista de dicts)

        # arquivos
        self.arquivos_alterados = []
        self.arquivos_protegidos = []    # testes que já existiam: não podem ser alterados
        self.arquivos_exigidos = []      # arquivos .py citados na tarefa: precisam existir
        self.originais = {}              # arquivo -> conteúdo que ele tinha antes da primeira alteração
        self.arquivos_vistos = set()     # arquivos cujo conteúdo o modelo viu na conversa atual da implementação

        # verificação
        self.testes_passaram = False
        self.exige_revisao = False       # se True, só vai para DONE com as duas revisões aprovadas
        self.revisoes = {"codigo": None, "testes": None}      # None: não revisou; True/False: resultado
        self.vetos = {}                  # "revisão:critério" -> quantas vezes essa revisão reprovou esse critério

        # reparo
        self.diagnosticar = False        # se True, uma falha de teste é diagnosticada antes do reparo
        self.testes_que_falharam = []    # nomes das funções de teste que falharam na última rodada
        self.testes_descartados = []     # testes escritos pelo modelo que o programa descartou no fim
        self.diagnostico = None          # resultado do último diagnóstico (dict com a classificação)
        self.restricao_escrita = None    # "testes" ou "codigo": o que o reparo pode alterar; None: tudo
        self.recusas_do_reparo = 0       # escritas recusadas pela restrição neste reparo

        # limites e contadores
        self.max_tentativas = max_tentativas
        self.max_iteracoes = max_iteracoes
        self.tentativas = 0
        self.iteracoes = 0
        self.chamadas_llm = 0

        # depuração
        self.depurar = False             # DEBUG: grava o fluxo completo em .minicode/debug.jsonl
        self.seq_debug = 0               # DEBUG

    def mudar_para(self, novo):
        if novo not in TRANSICOES[self.estado]:
            raise TransicaoInvalida(f"{self.estado} -> {novo} não é permitido")

        # hard gates: condições que precisam ser verdadeiras para entrar no novo estado
        if novo == SPECIFIED and not self.spec:
            raise TransicaoInvalida("sem especificação não vai para SPECIFIED")

        if novo == PLANNED and not self.plano:
            raise TransicaoInvalida("sem plano não vai para PLANNED")

        if novo == TEST_PLANNED and not self.plano_de_testes:
            raise TransicaoInvalida("sem plano de testes não vai para TEST_PLANNED")

        if novo == VERIFYING and not self.arquivos_alterados:
            raise TransicaoInvalida("nenhum arquivo foi alterado, não há o que verificar")

        if novo == VERIFYING:
            # os arquivos citados no pedido precisam existir exatamente no caminho citado
            for caminho in self.arquivos_exigidos:
                if not (Path(self.raiz) / caminho).is_file():
                    raise TransicaoInvalida(f"o arquivo {caminho}, citado na tarefa, não existe nesse caminho. Crie-o exatamente em {caminho}.")

        if novo == DONE and not self.testes_passaram:
            raise TransicaoInvalida("sem testes passando não vai para DONE")

        if novo == DONE and self.exige_revisao and not all(r is True for r in self.revisoes.values()):
            raise TransicaoInvalida("sem as revisões contra a especificação aprovadas não vai para DONE")

        if novo == DIAGNOSING and self.testes_passaram:
            raise TransicaoInvalida("os testes passaram, não há falha para diagnosticar")

        if novo == REPAIRING and self.estado in (DIAGNOSING, TEST_PLANNED) and not self.diagnostico:
            raise TransicaoInvalida("sem diagnóstico da falha não vai para REPAIRING")

        if novo == TEST_PLANNED and self.estado == DIAGNOSING and not self.diagnostico:
            raise TransicaoInvalida("sem diagnóstico apontando o plano de testes não volta para TEST_PLANNED")

        if novo == REPAIRING:
            # há o que reparar se os testes falharam OU se alguma revisão contra a spec reprovou
            reprovou = any(r is False for r in self.revisoes.values())
            if self.testes_passaram and not reprovou:
                raise TransicaoInvalida("os testes passaram, não há o que reparar")
            if self.tentativas >= self.max_tentativas:
                raise TransicaoInvalida("limite de tentativas de reparo atingido")
            self.tentativas += 1
            self.recusas_do_reparo = 0

        if novo == VERIFYING:
            # um diagnóstico e sua restrição valem só para o reparo que acabou de terminar
            self.diagnostico = None
            self.restricao_escrita = None

        self.estado = novo

    def acao_permitida(self, ferramenta):
        return ferramenta in FERRAMENTAS_POR_ESTADO[self.estado]

    def registrar_escrita(self, caminho):
        # qualquer escrita invalida o resultado dos testes e da revisão anteriores
        if caminho not in self.arquivos_alterados:
            self.arquivos_alterados.append(caminho)
        self.testes_passaram = False
        self.revisoes = {"codigo": None, "testes": None}

    def registrar_testes(self, passou):
        self.testes_passaram = passou

    def pode_recusar(self):
        # Conta uma escrita recusada neste reparo. Passou de MAX_RECUSAS_POR_REPARO, a restrição
        # é levantada (e a escrita deixa de ser recusada) para o reparo não virar um laço.
        self.recusas_do_reparo += 1
        if self.recusas_do_reparo > MAX_RECUSAS_POR_REPARO:
            self.restricao_escrita = None
            return False
        return True

    def registrar_diagnostico(self, diagnostico, restringir=True):
        # TEST_BUG e PLAN_BUG: o reparo só pode alterar testes. CODE_BUG: só o código.
        # Nos outros casos (ou se restringir=False) o reparo pode alterar tudo.
        self.diagnostico = diagnostico
        self.restricao_escrita = None
        if restringir and diagnostico["classificacao"] in (TEST_BUG, PLAN_BUG):
            self.restricao_escrita = "testes"
        elif restringir and diagnostico["classificacao"] == CODE_BUG:
            self.restricao_escrita = "codigo"

    def registrar_revisao(self, quem, aprovada):
        # quem: "codigo" (revisão antes dos testes) ou "testes" (revisão depois que passam)
        self.revisoes[quem] = aprovada

    def contar_iteracao(self):
        # chamado a cada volta do loop; passou do limite, a execução falha
        self.iteracoes += 1
        if self.iteracoes > self.max_iteracoes:
            self.mudar_para(FAILED)

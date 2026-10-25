import json
from datetime import datetime
from pathlib import Path


# Tudo é gravado em <raiz do projeto>/.minicode/

def pasta_registro(raiz):
    return Path(raiz) / ".minicode"


def iniciar_registro(raiz, tarefa):
    pasta_registro(raiz).mkdir(exist_ok=True)
    # começa uma execução nova: apaga os eventos da anterior
    (pasta_registro(raiz) / "actions.jsonl").write_text("", encoding="utf-8")


def registrar_evento(raiz, evento):
    # uma linha de JSON por evento (formato .jsonl)
    evento = dict(evento)
    evento["hora"] = datetime.now().isoformat()
    linha = json.dumps(evento, ensure_ascii=False)

    with open(pasta_registro(raiz) / "actions.jsonl", "a", encoding="utf-8") as arquivo:
        arquivo.write(linha + "\n")


def salvar_documento(raiz, nome, texto):
    (pasta_registro(raiz) / nome).write_text(texto, encoding="utf-8")


def salvar_estado(raiz, execucao):
    estado = {
        "tarefa": execucao.tarefa,
        "estado": execucao.estado,
        "tentativas": execucao.tentativas,
        "iteracoes": execucao.iteracoes,
        "chamadas_llm": execucao.chamadas_llm,
        "arquivos_alterados": execucao.arquivos_alterados,
        "testes_passaram": execucao.testes_passaram,
    }
    texto = json.dumps(estado, ensure_ascii=False, indent=2)
    (pasta_registro(raiz) / "state.json").write_text(texto, encoding="utf-8")

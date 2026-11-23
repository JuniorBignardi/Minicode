"""Cliente do modelo professor (API compatível com OpenAI, por exemplo a da NVIDIA), com limite de taxa e contagem de tokens.

Lê MINICODE_API_BASE e MINICODE_API_KEY do .env. A chave nunca é impressa nem gravada em log.
O limite de taxa vale para todas as threads do processo: por padrão, no máximo 30 chamadas por minuto (o serviço aceita ~40).
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


# Janela deslizante de 60 s: guarda o instante das últimas chamadas e faz a thread esperar
# quando já houve `por_minuto` chamadas no último minuto.
class LimiteDeTaxa:
    def __init__(self, por_minuto):
        self.por_minuto = por_minuto
        self.instantes = deque()
        self.trava = threading.Lock()

    def esperar(self):
        while True:
            with self.trava:
                agora = time.time()
                # esquece as chamadas com mais de 1 minuto
                while self.instantes and agora - self.instantes[0] > 60:
                    self.instantes.popleft()
                if len(self.instantes) < self.por_minuto:
                    self.instantes.append(agora)
                    return
                # quanto falta para a chamada mais antiga sair da janela
                falta = 60 - (agora - self.instantes[0])
            time.sleep(max(falta, 0.2))


class Professor:
    def __init__(self, modelo, por_minuto=30, arquivo_de_uso=None, base=None, chave=None, tempo=180):
        # sem base e chave explícitas, lê o endereço e a chave do .env
        if base is None or chave is None:
            from dotenv import load_dotenv
            load_dotenv(RAIZ / ".env", override=True)
        self.base = (base or os.environ["MINICODE_API_BASE"]).rstrip("/")
        self.chave = chave or os.environ["MINICODE_API_KEY"]
        self.modelo, self.tempo = modelo, tempo
        self.limite = LimiteDeTaxa(por_minuto)
        self.arquivo_de_uso = Path(arquivo_de_uso) if arquivo_de_uso else None
        self.trava_do_log = threading.Lock()
        self.aceita_sem_pensar = True   # o parâmetro que desliga o raciocínio; desligado se o servidor o recusar

    # uma chamada HTTP ao endpoint /chat/completions
    def _enviar(self, corpo):
        req = urllib.request.Request(
            self.base + "/chat/completions",
            data=json.dumps(corpo).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.chave}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.tempo) as r:
            return json.loads(r.read().decode("utf-8"))

    # Chama o professor com até 4 tentativas: espera mais a cada falha de rede ou de servidor (429 e 5xx)
    # e desiste de vez com um erro de cliente.
    def __call__(self, mensagens, temperature=0.7, max_tokens=3000):
        ultimo_erro = None
        for tentativa in range(4):
            corpo = {
                "model": self.modelo,
                "messages": mensagens,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if self.aceita_sem_pensar:
                corpo["chat_template_kwargs"] = {"enable_thinking": False}
            self.limite.esperar()
            inicio = time.time()
            try:
                r = self._enviar(corpo)
                self._registrar(r, time.time() - inicio)
                return r["choices"][0]["message"].get("content") or ""
            except urllib.error.HTTPError as erro:
                ultimo_erro = f"HTTP {erro.code}"
                if erro.code == 400 and self.aceita_sem_pensar:
                    self.aceita_sem_pensar = False   # o servidor não conhece o parâmetro: repete sem ele
                    continue
                if erro.code == 429 or erro.code >= 500:
                    print(f"[aviso] HTTP {erro.code} do servidor, esperando {10 * (tentativa + 1)} s", flush=True)
                    time.sleep(10 * (tentativa + 1))
                    continue
                raise
            except (TimeoutError, urllib.error.URLError, json.JSONDecodeError) as erro:
                ultimo_erro = type(erro).__name__
                time.sleep(5 * (tentativa + 1))
        raise RuntimeError(f"professor sem resposta após 4 tentativas ({ultimo_erro})")

    # acrescenta uma linha por chamada ao arquivo de uso: modelo, tokens de entrada e de saída e segundos
    def _registrar(self, resposta, segundos):
        if not self.arquivo_de_uso:
            return
        uso = resposta.get("usage", {})
        linha = {
            "modelo": self.modelo,
            "entrada": uso.get("prompt_tokens", 0),
            "saida": uso.get("completion_tokens", 0),
            "segundos": round(segundos, 1),
        }
        # a trava impede que duas threads escrevam ao mesmo tempo no arquivo
        with self.trava_do_log:
            self.arquivo_de_uso.parent.mkdir(parents=True, exist_ok=True)
            with open(self.arquivo_de_uso, "a", encoding="utf-8") as f:
                f.write(json.dumps(linha) + "\n")

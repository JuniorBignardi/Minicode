from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# timeout de 60 s por tentativa (o padrão é 10 minutos), com até 2 novas tentativas
client = OpenAI(base_url=os.environ["MINICODE_API_BASE"], api_key=os.environ["MINICODE_API_KEY"],
                timeout=60, max_retries=2)

def chat_especialista():
    """Modelo especializado só para escrever o plano de testes (Parte 2). Devolve None se não estiver configurado.

    MINICODE_PLAN_API_BASE e MINICODE_PLAN_MODEL ligam o modelo; MINICODE_PLAN_API_KEY é opcional (servidor local não exige chave).
    """
    base, modelo = os.environ.get("MINICODE_PLAN_API_BASE"), os.environ.get("MINICODE_PLAN_MODEL")
    if not base or not modelo:
        return None
    cliente = OpenAI(base_url=base, api_key=os.environ.get("MINICODE_PLAN_API_KEY", "sem-chave"), timeout=120, max_retries=2)

    def chat_plano(mensagens, temperature=0, **kwargs):
        resposta = cliente.chat.completions.create(model=modelo, messages=mensagens, temperature=temperature, **kwargs)
        return resposta.choices[0].message.content

    return chat_plano


def chat(mensagens, temperature = 0, **kwargs):
    resposta = client.chat.completions.create(model=os.environ["MINICODE_MODEL"], messages = mensagens, temperature=temperature, **kwargs)

    return resposta.choices[0].message.content

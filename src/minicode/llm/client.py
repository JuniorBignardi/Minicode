from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# timeout de 60 s por tentativa (o padrão é 10 minutos), com até 2 novas tentativas
client = OpenAI(base_url=os.environ["MINICODE_API_BASE"], api_key=os.environ["MINICODE_API_KEY"],
                timeout=60, max_retries=2)

def chat(mensagens, temperature = 0, **kwargs):
    resposta = client.chat.completions.create(model=os.environ["MINICODE_MODEL"], messages = mensagens, temperature=temperature, **kwargs)

    return resposta.choices[0].message.content

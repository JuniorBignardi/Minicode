import json

def validar_acao(json):
    if isinstance(json, dict) and "tool" in json and "args" in json:
        return True
    return False


def extrair_acao(texto):
    try:
        json_final = json.loads(texto)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    try:
        texto_limpo = texto.replace("```json", "").replace("```", "")
        json_final = json.loads(texto_limpo)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    try:
        inicio = texto.find("{")
        final = texto.rfind("}") + 1
        texto_limpo = texto[inicio:final]
        json_final = json.loads(texto_limpo)
        if validar_acao(json_final):
            return json_final
    except json.JSONDecodeError:
        pass
    return None

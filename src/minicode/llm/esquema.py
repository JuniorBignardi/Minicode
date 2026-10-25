def esquema_acao(nomes_das_ferramentas, parametros):
    # JSON Schema da ação. O servidor aplica o schema durante a geração (response_format),
    # então o modelo fica incapaz de escrever JSON quebrado ou de pedir uma ferramenta
    # que não está na lista (o "enum").
    propriedades = {}
    for nome in nomes_das_ferramentas:
        for parametro in parametros[nome]:
            propriedades[parametro] = {"type": "string"}

    return {
        "type": "object",
        "properties": {
            "pensamento": {"type": "string"},
            "tool": {"type": "string", "enum": list(nomes_das_ferramentas)},
            "args": {"type": "object", "properties": propriedades, "additionalProperties": False},
        },
        "required": ["pensamento", "tool", "args"],
        "additionalProperties": False,
    }


def formato_da_resposta(esquema, nome="acao"):
    # o formato que a API da OpenAI espera no parâmetro response_format
    return {"type": "json_schema", "json_schema": {"name": nome, "schema": esquema}}

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_ai_response(message_content: str, tenant_name: str,
    store_context: str = "",
    products_context: str = "",
    faq_context: str = "", 
    history=None) -> str:
    system_prompt = f"""
    Você é uma atendente virtual do estabelecimento {tenant_name}.

    Regras:
    - Responda em português do Brasil
    - Seja simpática, natural e objetiva
    - Use emojis com moderação
    - Responda como um humano, não como robô
    - Nunca invente informações
    - Use apenas as informações fornecidas no contexto
    - Se houver produtos relevantes, use-os para responder
    - Se houver FAQ relevante, priorize essas respostas
    - Mantenha respostas curtas e úteis
    DADOS DO ESTABELECIMENTO:
    {store_context}

    PRODUTOS:
    {products_context}

    FAQ:
    {faq_context}
    """.strip()

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    if history:
        messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": message_content,
        }
    )
    print("MESSAGES ENVIADAS PARA OPENAI:")
    import json
    print(json.dumps(messages, indent=2, ensure_ascii=False))

    response = client.responses.create(
        model=MODEL,
        input=messages,
    )

    return response.output_text.strip() if response.output_text else "Desculpe, não consegui responder agora."
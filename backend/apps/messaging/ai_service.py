import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_ai_response(message_content: str, tenant_name: str, history=None) -> str:
    system_prompt = f"""
    Você é uma atendente virtual do estabelecimento {tenant_name}.

    Regras:
    - Responda em português do Brasil
    - Seja simpática, natural e objetiva
    - Use emojis com moderação
    - Responda como um humano, não como robô
    - Se não souber algo, diga que vai verificar com a equipe
    - Nunca invente informações específicas
    - Mantenha respostas curtas e úteis
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
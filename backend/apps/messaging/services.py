from apps.channels.models import TenantChannelAccount
from apps.conversations.models import Customer, CustomerChannelIdentity, Conversation
from apps.messaging.models import Message
from apps.knowledge.models import Store, Product, FAQItem
from .ai_service import generate_ai_response
import logging
from django.db.models import Q
import re
from apps.messaging.ai_reply_service import AIReplyService


logger = logging.getLogger(__name__)

def process_inbound_whatsapp_message(
    external_account_id: str,
    external_user_id: str,
    external_display_name: str,
    content: str,
):
    tenant_account = TenantChannelAccount.objects.select_related("tenant", "channel").get(
        external_account_id=external_account_id,
        channel__code="whatsapp",
        status="active",
    )

    identity = CustomerChannelIdentity.objects.filter(
        channel=tenant_account.channel,
        external_user_id=external_user_id,
        customer__tenant=tenant_account.tenant,
    ).select_related("customer").first()

    if identity:
        customer = identity.customer
        if external_display_name and identity.external_display_name != external_display_name:
            identity.external_display_name = external_display_name
            identity.save(update_fields=["external_display_name"])
    else:
        customer = Customer.objects.create(tenant=tenant_account.tenant)
        CustomerChannelIdentity.objects.create(
            customer=customer,
            channel=tenant_account.channel,
            external_user_id=external_user_id,
            external_display_name=external_display_name or "",
        )

    conversation = Conversation.objects.filter(
        tenant=tenant_account.tenant,
        customer=customer,
        channel=tenant_account.channel,
        status="open",
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            tenant=tenant_account.tenant,
            customer=customer,
            channel=tenant_account.channel,
            tenant_channel_account=tenant_account,
            status="open",
        )

    message = Message.objects.create(
        conversation=conversation,
        channel=tenant_account.channel,
        sender_type=Message.SenderType.CUSTOMER,
        direction=Message.Direction.INBOUND,
        content=content,
        message_type="text",
        ai_generated=False,
        review_status=Message.ReviewStatus.APPROVED,
    )
    # carrega as ultimas mensagens 
    last_messages = Message.objects.filter(
        conversation=conversation
    ).order_by("-id")[:5]

    history = []
    for msg in reversed(last_messages):
        role = "assistant" if msg.sender_type == "ai" else "user"
        history.append({
            "role": role,
            "content": msg.content,
        })
    # carregando o contexto de conhecimento para a IA
    store = Store.objects.filter(tenant=tenant_account.tenant).first()
    products = Product.objects.filter(tenant=tenant_account.tenant, disponivel=True)[:10]
    faqs = FAQItem.objects.filter(tenant=tenant_account.tenant)[:10]
    # products = get_relevant_products(tenant_account.tenant, content, limit=5)
    # faqs = get_relevant_faqs(tenant_account.tenant, content, limit=5)

    store_context = ""
    if store:
        store_context = f"""
    Nome: {store.nome}
    Descrição: {store.descricao}
    Horário: {store.horario_funcionamento}
    Endereço: {store.endereco}
    Taxa de entrega: {store.taxa_entrega}
    Formas de pagamento: {store.formas_pagamento}
    """.strip()

    products_context = "\n".join(
        [
            f"- {product.nome} | Categoria: {product.categoria} | Preço: R$ {product.preco} | Descrição: {product.descricao}"
            for product in products
        ]
    )

    faq_context = "\n".join(
        [
            f"- Pergunta: {faq.pergunta} | Resposta: {faq.resposta}"
            for faq in faqs
        ]
    )


    # ai_response_text = generate_ai_response(content)
    try:
        ai_response_text = generate_ai_response(
        message_content=content,
        store_context=store_context,
        products_context=products_context,
        faq_context=faq_context,
        tenant_name=tenant_account.tenant.name,history=history
        )
    except Exception as e:
        logger.exception("Erro ao chamar OpenAI")
        ai_response_text = f"Recebemos sua mensagem e vamos encaminhar para atendimento. [erro: {str(e)}]"


    try:
        result = AIReplyService.handle_ai_response(
            conversation=conversation,
            channel=tenant_account.channel,
            ai_text=ai_response_text,
        )
    except Exception as e:
        logger.exception("Erro ao processar resposta da IA / envio automático")
        result = {
            "status": "error",
            "message_id": None,
            "detail": str(e),
        }

    # ai_message = Message.objects.create(
    #     conversation=conversation,
    #     channel=tenant_account.channel,
    #     sender_type=Message.SenderType.AI,
    #     direction=Message.Direction.OUTBOUND,
    #     content=ai_response_text,
    #     message_type="text",
    #     ai_generated=True,
    #     review_status=Message.ReviewStatus.PENDING,
    # )




    return {
    "tenant_id": tenant_account.tenant.id,
    "conversation_id": conversation.id,
    "message_id": message.id,
    "ai_message_id": result.get("message_id"),
    "ai_status": result.get("status"),
    "ai_detail": result.get("detail"),
    "customer_id": customer.id,
    }

# def generate_ai_response(message_content: str) -> str:
#     return f"Resposta automática: recebemos sua mensagem '{message_content}'"


#carregas apenas informaçoes relevantes para o contexto da OpenAI
def get_relevant_products(tenant, query, limit=5):
    keywords = extract_keywords(query)
    queryset = Product.objects.filter(tenant=tenant, disponivel=True)

    if not keywords:
        return queryset[:limit]

    q_objects = Q()
    for keyword in keywords:
        q_objects |= Q(nome__icontains=keyword)
        q_objects |= Q(descricao__icontains=keyword)
        q_objects |= Q(categoria__icontains=keyword)

    return queryset.filter(q_objects).distinct()[:limit]


def get_relevant_faqs(tenant, query, limit=5):
    keywords = extract_keywords(query)
    queryset = FAQItem.objects.filter(tenant=tenant)

    if not keywords:
        return queryset[:limit]

    q_objects = Q()
    for keyword in keywords:
        q_objects |= Q(pergunta__icontains=keyword)
        q_objects |= Q(resposta__icontains=keyword)

    return queryset.filter(q_objects).distinct()[:limit]



def extract_keywords(text: str):
    words = re.findall(r"\w+", text.lower())
    stopwords = {
        "a", "o", "e", "de", "do", "da", "das", "dos", "para", "com",
        "tem", "têm", "vocês", "voces", "uma", "um", "as", "os",
        "que", "qual", "quais", "quanto", "custa", "aceita", "aceitam"
    }
    return [word for word in words if len(word) > 2 and word not in stopwords]

def detect_intent(text: str) -> str:
    text = (text or "").lower()

    product_words = [
        "produto", "produtos", "cardápio", "cardapio", "menu", "item", "itens",
        "pizza", "lanche", "bebida", "sobremesa", "prato", "pratos"
    ]
    hours_words = [
        "horário", "horario", "funcionamento", "abre", "abrem", "fecha", "fecham"
    ]
    price_words = [
        "preço", "preco", "valor", "valores", "quanto custa", "quanto é", "quanto eh"
    ]
    delivery_words = [
        "entrega", "delivery", "entregam", "taxa de entrega", "frete"
    ]
    payment_words = [
        "pagamento", "pagamentos", "pix", "cartão", "cartao", "dinheiro", "aceita"
    ]
    location_words = [
        "endereço", "endereco", "localização", "localizacao", "onde fica", "local"
    ]

    if any(word in text for word in product_words):
        return "products"

    if any(word in text for word in hours_words):
        return "hours"

    if any(word in text for word in price_words):
        return "pricing"

    if any(word in text for word in delivery_words):
        return "delivery"

    if any(word in text for word in payment_words):
        return "payment"

    if any(word in text for word in location_words):
        return "location"

    return "general"

def build_products_context(products) -> str:
    if not products:
        return "Nenhum produto relevante encontrado."

    lines = ["PRODUTOS RELEVANTES ENCONTRADOS:"]
    for product in products:
        nome = getattr(product, "nome", "") or getattr(product, "name", "") or "Produto sem nome"
        descricao = getattr(product, "descricao", "") or ""
        categoria = getattr(product, "categoria", "") or ""
        preco = getattr(product, "preco", None)

        line = f"- {nome}"

        if categoria:
            line += f" | categoria: {categoria}"

        if preco not in [None, ""]:
            line += f" | preço: R$ {preco}"

        if descricao:
            line += f" | descrição: {descricao}"

        lines.append(line)

    return "\n".join(lines)
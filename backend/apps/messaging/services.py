from apps.channels.models import TenantChannelAccount
from apps.conversations.models import Customer, CustomerChannelIdentity, Conversation
from apps.messaging.models import Message
from .ai_service import generate_ai_response
import logging

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
        review_status=Message.ReviewStatus.PENDING,
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

    # ai_response_text = generate_ai_response(content)
    try:
        ai_response_text = generate_ai_response(
        message_content=content,
        tenant_name=tenant_account.tenant.name,history=history
        )
    except Exception as e:
        logger.exception("Erro ao chamar OpenAI")
        ai_response_text = f"Recebemos sua mensagem e vamos encaminhar para atendimento. [erro: {str(e)}]"


    ai_message = Message.objects.create(
        conversation=conversation,
        channel=tenant_account.channel,
        sender_type=Message.SenderType.AI,
        direction=Message.Direction.OUTBOUND,
        content=ai_response_text,
        message_type="text",
        ai_generated=True,
        review_status=Message.ReviewStatus.PENDING,
    )

    return {
        "tenant_id": tenant_account.tenant.id,
        "conversation_id": conversation.id,
        "message_id": message.id,
        "ai_message_id": ai_message.id,
        "customer_id": customer.id,
    }

# def generate_ai_response(message_content: str) -> str:
#     return f"Resposta automática: recebemos sua mensagem '{message_content}'"




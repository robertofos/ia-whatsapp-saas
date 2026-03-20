from apps.messaging.models import Message
from apps.messaging.whatsapp_service import WhatsAppService
from apps.tenants.models import Tenant


class AIReplyService:
    @staticmethod
    def handle_ai_response(conversation, channel, ai_text: str):
        tenant = conversation.tenant

        print("DEBUG tenant.ai_review_mode =", tenant.ai_review_mode)
        print("DEBUG Tenant.REVIEW_MODE_AUTO =", Tenant.REVIEW_MODE_AUTO)

        if tenant.ai_review_mode == Tenant.REVIEW_MODE_AUTO:
            tenant_account = conversation.tenant_channel_account

            if not tenant_account:
                raise ValueError("Conversation sem tenant_channel_account vinculado")

            customer_identity = conversation.customer.identities.filter(
                channel=conversation.channel
            ).first()

            if not customer_identity:
                raise ValueError("Identidade do cliente para este canal não encontrada")

            destination = customer_identity.external_user_id

            if not destination:
                raise ValueError("Identidade do cliente sem external_user_id")

            send_result = WhatsAppService.send_text(
                to=destination,
                body=ai_text,
                tenant_account=tenant_account,
            )

            if not send_result.get("success"):
                raise ValueError(
                    send_result.get("detail", "Falha ao enviar mensagem no WhatsApp")
                )

            message = Message.objects.create(
                conversation=conversation,
                channel=channel,
                sender_type=Message.SenderType.AI,
                direction=Message.Direction.OUTBOUND,
                content=ai_text,
                message_type="text",
                ai_generated=True,
                review_status=Message.ReviewStatus.APPROVED,
            )

            print(f"[AUTO] Mensagem enviada automaticamente: {message.id}")

            return {
                "status": "sent",
                "message_id": message.id,
                "send_result": send_result,
            }

        message = Message.objects.create(
            conversation=conversation,
            channel=channel,
            sender_type=Message.SenderType.AI,
            direction=Message.Direction.OUTBOUND,
            content=ai_text,
            message_type="text",
            ai_generated=True,
            review_status=Message.ReviewStatus.PENDING,
        )

        print(f"[REVIEW] Mensagem pendente: {message.id}")

        return {
            "status": "pending_review",
            "message_id": message.id,
        }
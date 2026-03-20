from apps.messaging.models import Message
from apps.tenants.models import Tenant


class AIReplyService:
    @staticmethod
    def handle_ai_response(conversation, channel, ai_text: str):
        tenant = conversation.tenant

        print("DEBUG tenant.ai_review_mode =", tenant.ai_review_mode)
        print("DEBUG Tenant.REVIEW_MODE_AUTO =", Tenant.REVIEW_MODE_AUTO)

        if tenant.ai_review_mode == Tenant.REVIEW_MODE_AUTO:
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

            print(f"[AUTO] Mensagem criada automaticamente: {message.id}")

            return {
                "status": "sent",
                "message_id": message.id,
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
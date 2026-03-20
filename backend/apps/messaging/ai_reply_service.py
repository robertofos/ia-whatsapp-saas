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

            message = Message.objects.create(
                conversation=conversation,
                channel=channel,
                sender_type=Message.SenderType.AI,
                direction=Message.Direction.OUTBOUND,
                content=ai_text,
                message_type="text",
                ai_generated=True,
                review_status=Message.ReviewStatus.APPROVED,
                delivery_status=send_result.get(
                    "delivery_status",
                    Message.DeliveryStatus.FAILED,
                ),
                provider_message_id=send_result.get("provider_message_id", ""),
                sent_at=send_result.get("sent_at"),
                send_error=send_result.get("send_error", ""),
            )

            if not send_result.get("success"):
                print(f"[AUTO][ERROR] Falha no envio automático: {message.id}")
                return {
                    "status": "error",
                    "message_id": message.id,
                    "detail": send_result.get(
                        "send_error",
                        "Falha ao enviar mensagem no WhatsApp",
                    ),
                    "delivery_status": message.delivery_status,
                }

            print(f"[AUTO] Mensagem enviada automaticamente: {message.id}")

            return {
                "status": "sent",
                "message_id": message.id,
                "delivery_status": message.delivery_status,
                "provider_message_id": message.provider_message_id,
                "sent_at": message.sent_at,
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
            delivery_status=Message.DeliveryStatus.NOT_SENT,
            provider_message_id="",
            sent_at=None,
            send_error="",
        )

        print(f"[REVIEW] Mensagem pendente: {message.id}")

        return {
            "status": "pending_review",
            "message_id": message.id,
            "delivery_status": message.delivery_status,
        }
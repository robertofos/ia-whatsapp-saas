from django.utils import timezone
from apps.messaging.models import Message


class WhatsAppWebhookService:

    @classmethod
    def handle(cls, payload: dict):
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # 📩 mensagens recebidas (inbound)
                for message in value.get("messages", []):
                    cls._handle_inbound(message, value, payload)

                # 📊 status (sent, delivered, read, failed)
                for status_item in value.get("statuses", []):
                    cls._handle_status(status_item, payload)

    # =========================
    # 📩 INBOUND MESSAGE
    # =========================
    @classmethod
    def _handle_inbound(cls, message_data, value, raw_payload):
        from_number = message_data.get("from")
        message_id = message_data.get("id")

        text_body = ""
        if message_data.get("type") == "text":
            text_body = message_data.get("text", {}).get("body", "")

        # ⚠️ aqui depois vamos ligar com Customer/Identity
        # por enquanto só salvar simples

        Message.objects.create(
            conversation_id=None,  # ajustar depois
            channel_id=1,  # ⚠️ ajustar para seu channel whatsapp
            external_message_id=message_id,
            sender_type="customer",
            direction="inbound",
            content=text_body,
            delivery_status="sent",
            raw_payload_json=raw_payload,
        )

    # =========================
    # 📊 STATUS UPDATE
    # =========================
    @classmethod
    def _handle_status(cls, status_data, raw_payload):
        message_id = status_data.get("id")
        status = status_data.get("status")

        message = Message.objects.filter(
            provider_message_id=message_id
        ).first()

        if not message:
            return

        message.provider_status = status
        message.raw_payload_json = raw_payload

        if status == "sent":
            message.delivery_status = "sent"
            if not message.sent_at:
                message.sent_at = timezone.now()

        elif status == "delivered":
            message.delivery_status = "delivered"
            if not message.delivered_at:
                message.delivered_at = timezone.now()

        elif status == "read":
            message.delivery_status = "read"
            if not message.read_at:
                message.read_at = timezone.now()

        elif status == "failed":
            message.delivery_status = "failed"
            if not message.failed_at:
                message.failed_at = timezone.now()

            errors = status_data.get("errors", [])
            if errors:
                message.send_error = errors[0].get("title", "")

        message.save()
from django.utils import timezone

from apps.channels.models import Channel
from apps.messaging.models import Message
from apps.messaging.services import process_inbound_whatsapp_message


class WhatsAppWebhookService:

    @classmethod
    def handle(cls, payload: dict):
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                for message in value.get("messages", []):
                    cls._handle_inbound(message, value, payload)

                for status_item in value.get("statuses", []):
                    cls._handle_status(status_item, payload)

    @classmethod
    def _handle_inbound(cls, message_data, value, raw_payload):
        message_id = message_data.get("id")
        from_number = message_data.get("from")
        text_body = ""

        if message_data.get("type") == "text":
            text_body = message_data.get("text", {}).get("body", "")

        if not from_number or not text_body:
            return

        metadata = value.get("metadata", {})
        external_account_id = (
            metadata.get("phone_number_id")
            or metadata.get("display_phone_number")
            or "whatsapp-default"
        )

        contacts = value.get("contacts", [])
        external_display_name = ""

        if contacts:
            external_display_name = (
                contacts[0].get("profile", {}).get("name", "") or ""
            )

        result = process_inbound_whatsapp_message(
            external_account_id=external_account_id,
            external_user_id=from_number,
            external_display_name=external_display_name,
            content=text_body,
        )

        print("RESULT PROCESS:", result)

        message_obj = None

        if isinstance(result, dict):
            if "message" in result and isinstance(result["message"], dict):
                message_obj = Message.objects.filter(id=result["message"].get("id")).first()
            elif "message_id" in result:
                message_obj = Message.objects.filter(id=result.get("message_id")).first()

        if message_obj:
            message_obj.external_message_id = message_id
            message_obj.raw_payload_json = raw_payload
            message_obj.save(update_fields=["external_message_id", "raw_payload_json", "updated_at"])

    @classmethod
    def _handle_status(cls, status_data, raw_payload):
        provider_message_id = status_data.get("id")
        provider_status = status_data.get("status")

        message = Message.objects.filter(
            provider_message_id=provider_message_id
        ).first()

        if not message:
            return

        message.provider_status = provider_status
        message.raw_payload_json = raw_payload

        if provider_status == "sent":
            message.delivery_status = Message.DeliveryStatus.SENT
            if not message.sent_at:
                message.sent_at = timezone.now()

        elif provider_status == "delivered":
            message.delivery_status = Message.DeliveryStatus.DELIVERED
            if not message.delivered_at:
                message.delivered_at = timezone.now()

        elif provider_status == "read":
            message.delivery_status = Message.DeliveryStatus.READ
            if not message.read_at:
                message.read_at = timezone.now()

        elif provider_status == "failed":
            message.delivery_status = Message.DeliveryStatus.FAILED
            if not message.failed_at:
                message.failed_at = timezone.now()

            errors = status_data.get("errors", [])
            if errors:
                message.send_error = errors[0].get("title", "") or str(errors[0])

        message.save(update_fields=[
            "provider_status",
            "raw_payload_json",
            "delivery_status",
            "sent_at",
            "delivered_at",
            "read_at",
            "failed_at",
            "send_error",
            "updated_at",
        ])
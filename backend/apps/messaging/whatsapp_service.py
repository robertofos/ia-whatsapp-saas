import logging
import requests

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsAppService:
    @staticmethod
    def send_text(to: str, body: str, tenant_account):
        if not tenant_account:
            return {
                "success": False,
                "delivery_status": "failed",
                "provider_message_id": "",
                "sent_at": None,
                "send_error": "tenant_account não informado",
            }

        if tenant_account.channel.code != "whatsapp":
            return {
                "success": False,
                "delivery_status": "failed",
                "provider_message_id": "",
                "sent_at": None,
                "send_error": f"Canal inválido para WhatsAppService: {tenant_account.channel.code}",
            }

        access_token = getattr(tenant_account, "access_token", "") or settings.WHATSAPP_ACCESS_TOKEN
        phone_number_id = tenant_account.external_account_id

        if not access_token:
            return {
                "success": False,
                "delivery_status": "failed",
                "provider_message_id": "",
                "sent_at": None,
                "send_error": "WHATSAPP_ACCESS_TOKEN não configurado",
            }

        if not phone_number_id:
            return {
                "success": False,
                "delivery_status": "failed",
                "provider_message_id": "",
                "sent_at": None,
                "send_error": "external_account_id/phone_number_id não configurado",
            }

        logger.info(
            "[WhatsAppService] Enviando mensagem para %s | tenant=%s | conta=%s | body=%s",
            to,
            tenant_account.tenant_id,
            phone_number_id,
            body,
        )

        print(
            f"[WHATSAPP SEND REAL] tenant={tenant_account.tenant_id} "
            f"account={phone_number_id} to={to} body={body}"
        )

        url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": body,
            },
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            print("WHATSAPP STATUS CODE:", response.status_code)
            print("WHATSAPP RESPONSE TEXT:", response.text)

            data = response.json()

            if not response.ok:
                error = data.get("error", {})
                return {
                    "success": False,
                    "provider": "whatsapp",
                    "provider_message_id": "",
                    "delivery_status": "failed",
                    "sent_at": None,
                    "send_error": error.get("message", str(data)),
                    "raw_response": data,
                }

            provider_message_id = ""
            messages = data.get("messages", [])
            if messages:
                provider_message_id = messages[0].get("id", "")

            return {
                "success": True,
                "provider": "whatsapp",
                "provider_message_id": provider_message_id,
                "delivery_status": "sent",
                "sent_at": timezone.now(),
                "send_error": "",
                "to": to,
                "body": body,
                "external_account_id": phone_number_id,
                "raw_response": data,
            }

        except Exception as exc:
            logger.exception("Erro ao enviar mensagem WhatsApp")
            return {
                "success": False,
                "provider": "whatsapp",
                "provider_message_id": "",
                "delivery_status": "failed",
                "sent_at": None,
                "send_error": str(exc),
            }
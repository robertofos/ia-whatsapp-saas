import logging
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

        logger.info(
            "[WhatsAppService] Enviando mensagem para %s | tenant=%s | conta=%s | body=%s",
            to,
            tenant_account.tenant_id,
            tenant_account.external_account_id,
            body,
        )

        print(
            f"[WHATSAPP SEND] tenant={tenant_account.tenant_id} "
            f"account={tenant_account.external_account_id} to={to} body={body}"
        )

        fake_provider_message_id = f"mock-{timezone.now().timestamp()}"

        return {
            "success": True,
            "provider": "mock",
            "provider_message_id": fake_provider_message_id,
            "delivery_status": "sent",
            "sent_at": timezone.now(),
            "send_error": "",
            "to": to,
            "body": body,
            "external_account_id": tenant_account.external_account_id,
        }
# apps/messaging/whatsapp_service.py
import logging

logger = logging.getLogger(__name__)


class WhatsAppService:
    @staticmethod
    def send_text(to: str, body: str, tenant_account):
        if not tenant_account:
            return {
                "success": False,
                "detail": "tenant_account não informado",
            }

        if tenant_account.channel.code != "whatsapp":
            return {
                "success": False,
                "detail": f"Canal inválido para WhatsAppService: {tenant_account.channel.code}",
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

        return {
            "success": True,
            "provider": "mock",
            "to": to,
            "body": body,
            "external_account_id": tenant_account.external_account_id,
        }
from django.conf import settings
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny


from .services.whatsapp_webhook_service import WhatsAppWebhookService


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    # ✅ VERIFICAÇÃO META (GET)
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)

        return Response({"detail": "Invalid verify token"}, status=403)

    # ✅ RECEBER EVENTOS (POST)
    WhatsAppWebhookService.handle(request.data)

    return Response({"ok": True}, status=status.HTTP_200_OK)


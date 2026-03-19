from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Message
from .serializers import MessageSerializer
from .services import process_inbound_whatsapp_message

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all().order_by("id")
    serializer_class = MessageSerializer

@api_view(["POST"])
def whatsapp_webhook_mock(request):
    required_fields = ["external_account_id", "external_user_id", "content"]
    missing = [field for field in required_fields if not request.data.get(field)]

    if missing:
        return Response(
            {"detail": f"Campos obrigatórios ausentes: {', '.join(missing)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = process_inbound_whatsapp_message(
        external_account_id=request.data["external_account_id"],
        external_user_id=request.data["external_user_id"],
        external_display_name=request.data.get("external_display_name", ""),
        content=request.data["content"],
    )

    return Response(result, status=status.HTTP_201_CREATED)
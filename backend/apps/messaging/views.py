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

@api_view(["GET"])
def pending_messages_view(request):
    tenant_id = request.GET.get("tenant_id")

    if not tenant_id:
        return Response({"detail": "tenant_id é obrigatório"}, status=400)

    messages = Message.objects.filter(
        conversation__tenant_id=tenant_id,
        sender_type=Message.SenderType.AI,
        direction=Message.Direction.OUTBOUND,
        review_status=Message.ReviewStatus.PENDING,
    ).order_by("created_at")

    data = [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "content": m.content,
            "created_at": m.created_at,
        }
        for m in messages
    ]

    return Response(data)

@api_view(["POST"])
def approve_message_view(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({"detail": "Mensagem não encontrada"}, status=404)

    if message.review_status != Message.ReviewStatus.PENDING:
        return Response(
            {"detail": f"Mensagem não está pendente. Status: {message.review_status}"},
            status=400,
        )

    message.review_status = Message.ReviewStatus.APPROVED
    message.save()

    # 🔥 aqui futuramente envia pro WhatsApp real

    return Response({
        "detail": "Mensagem aprovada com sucesso",
        "message_id": message.id,
        "status": "approved"
    })

@api_view(["POST"])
def reject_message_view(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({"detail": "Mensagem não encontrada"}, status=404)

    if message.review_status != Message.ReviewStatus.PENDING:
        return Response(
            {"detail": f"Mensagem não está pendente. Status: {message.review_status}"},
            status=400,
        )

    message.review_status = Message.ReviewStatus.REJECTED
    message.save()

    return Response({
        "detail": "Mensagem rejeitada",
        "message_id": message.id,
        "status": "rejected"
    })

@api_view(["POST"])
def edit_and_approve_message_view(request, message_id):
    new_content = request.data.get("content")

    if not new_content:
        return Response({"detail": "content é obrigatório"}, status=400)

    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({"detail": "Mensagem não encontrada"}, status=404)

    if message.review_status != Message.ReviewStatus.PENDING:
        return Response(
            {"detail": f"Mensagem não está pendente. Status: {message.review_status}"},
            status=400,
        )

    message.content = new_content
    message.review_status = Message.ReviewStatus.APPROVED
    message.save()

    return Response({
        "detail": "Mensagem editada e aprovada",
        "message_id": message.id,
        "content": message.content,
    })
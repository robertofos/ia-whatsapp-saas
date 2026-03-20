from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Message
from .serializers import MessageSerializer
from .services import process_inbound_whatsapp_message
from apps.messaging.whatsapp_service import WhatsAppService

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
        message = Message.objects.select_related(
            "conversation",
            "conversation__tenant",
            "conversation__channel",
            "conversation__tenant_channel_account",
            "conversation__tenant_channel_account__channel",
            "conversation__customer",
            "channel",
        ).get(id=message_id)
    except Message.DoesNotExist:
        return Response({"detail": "Mensagem não encontrada"}, status=404)

    if message.review_status != Message.ReviewStatus.PENDING:
        return Response(
            {"detail": f"Mensagem não está pendente. Status: {message.review_status}"},
            status=400,
        )

    conversation = message.conversation
    tenant_account = conversation.tenant_channel_account

    if not tenant_account:
        return Response(
            {"detail": "Conversation sem tenant_channel_account vinculado"},
            status=400,
        )

    customer_identity = conversation.customer.identities.filter(
        channel=conversation.channel
    ).first()

    if not customer_identity:
        return Response(
            {"detail": "Identidade do cliente para este canal não encontrada"},
            status=400,
        )

    destination = customer_identity.external_user_id

    if not destination:
        return Response(
            {"detail": "Identidade do cliente sem external_user_id"},
            status=400,
        )

    send_result = WhatsAppService.send_text(
        to=destination,
        body=message.content,
        tenant_account=tenant_account,
    )

    message.review_status = Message.ReviewStatus.APPROVED
    message.delivery_status = send_result.get(
        "delivery_status",
        Message.DeliveryStatus.FAILED,
    )
    message.provider_message_id = send_result.get("provider_message_id", "")
    message.sent_at = send_result.get("sent_at")
    message.send_error = send_result.get("send_error", "")

    message.save()

    if not send_result.get("success"):
        return Response(
            {
                "detail": send_result.get("send_error", "Falha ao enviar mensagem no WhatsApp"),
                "message_id": message.id,
                "review_status": message.review_status,
                "delivery_status": message.delivery_status,
            },
            status=502,
        )

    return Response(
        {
            "detail": "Mensagem aprovada e enviada com sucesso",
            "message_id": message.id,
            "status": message.review_status,
            "delivery_status": message.delivery_status,
            "provider_message_id": message.provider_message_id,
            "sent_at": message.sent_at,
            "send_result": send_result,
        }
    )

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
        message = Message.objects.select_related(
            "conversation",
            "conversation__tenant",
            "conversation__channel",
            "conversation__tenant_channel_account",
            "conversation__tenant_channel_account__channel",
            "conversation__customer",
            "channel",
        ).get(id=message_id)
    except Message.DoesNotExist:
        return Response({"detail": "Mensagem não encontrada"}, status=404)

    if message.review_status != Message.ReviewStatus.PENDING:
        return Response(
            {"detail": f"Mensagem não está pendente. Status: {message.review_status}"},
            status=400,
        )

    conversation = message.conversation
    tenant_account = conversation.tenant_channel_account

    if not tenant_account:
        return Response(
            {"detail": "Conversation sem tenant_channel_account vinculado"},
            status=400,
        )

    customer_identity = conversation.customer.identities.filter(
        channel=conversation.channel
    ).first()

    if not customer_identity:
        return Response(
            {"detail": "Identidade do cliente para este canal não encontrada"},
            status=400,
        )

    destination = customer_identity.external_user_id

    if not destination:
        return Response(
            {"detail": "Identidade do cliente sem external_user_id"},
            status=400,
        )

    message.content = new_content

    send_result = WhatsAppService.send_text(
        to=destination,
        body=message.content,
        tenant_account=tenant_account,
    )

    message.review_status = Message.ReviewStatus.EDITED
    message.delivery_status = send_result.get(
        "delivery_status",
        Message.DeliveryStatus.FAILED,
    )
    message.provider_message_id = send_result.get("provider_message_id", "")
    message.sent_at = send_result.get("sent_at")
    message.send_error = send_result.get("send_error", "")

    message.save()

    if not send_result.get("success"):
        return Response(
            {
                "detail": send_result.get("send_error", "Falha ao enviar mensagem no WhatsApp"),
                "message_id": message.id,
                "review_status": message.review_status,
                "delivery_status": message.delivery_status,
            },
            status=502,
        )

    return Response(
        {
            "detail": "Mensagem editada, aprovada e enviada com sucesso",
            "message_id": message.id,
            "content": message.content,
            "status": message.review_status,
            "delivery_status": message.delivery_status,
            "provider_message_id": message.provider_message_id,
            "sent_at": message.sent_at,
            "send_result": send_result,
        }
    )

@api_view(["GET"])
def edited_messages_view(request):
    tenant_id = request.GET.get("tenant_id")

    if not tenant_id:
        return Response({"detail": "tenant_id é obrigatório"}, status=400)

    messages = Message.objects.filter(
        conversation__tenant_id=tenant_id,
        sender_type=Message.SenderType.AI,
        direction=Message.Direction.OUTBOUND,
        review_status=Message.ReviewStatus.EDITED,
    ).order_by("-created_at")

    data = [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "content": m.content,
            "review_status": m.review_status,
            "created_at": m.created_at,
        }
        for m in messages
    ]

    return Response(data)

@api_view(["GET"])
def rejected_messages_view(request):
    tenant_id = request.GET.get("tenant_id")

    if not tenant_id:
        return Response({"detail": "tenant_id é obrigatório"}, status=400)

    messages = Message.objects.filter(
        conversation__tenant_id=tenant_id,
        sender_type=Message.SenderType.AI,
        direction=Message.Direction.OUTBOUND,
        review_status=Message.ReviewStatus.REJECTED,
    ).order_by("-created_at")

    data = [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "content": m.content,
            "review_status": m.review_status,
            "created_at": m.created_at,
        }
        for m in messages
    ]

    return Response(data)

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.messaging.models import Message


@api_view(["GET"])
def reviewed_messages_view(request):
    tenant_id = request.GET.get("tenant_id")
    status_filter = request.GET.get("status")
    channel_filter = request.GET.get("channel")
    conversation_id = request.GET.get("conversation_id")
    search = request.GET.get("search")

    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 10)

    if not tenant_id:
        return Response({"detail": "tenant_id é obrigatório"}, status=400)

    valid_statuses = {
        "pending": Message.ReviewStatus.PENDING,
        "approved": Message.ReviewStatus.APPROVED,
        "edited": Message.ReviewStatus.EDITED,
        "rejected": Message.ReviewStatus.REJECTED,
    }

    valid_channels = {
        "whatsapp": "whatsapp",
        "instagram": "instagram",
        "facebook": "facebook",
        "google": "google",
    }

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {"detail": "page e page_size devem ser numéricos"},
            status=400,
        )

    if page < 1:
        return Response({"detail": "page deve ser maior ou igual a 1"}, status=400)

    if page_size < 1 or page_size > 100:
        return Response(
            {"detail": "page_size deve estar entre 1 e 100"},
            status=400,
        )

    messages = Message.objects.filter(
        conversation__tenant_id=tenant_id,
        sender_type=Message.SenderType.AI,
        direction=Message.Direction.OUTBOUND,
    ).select_related("channel", "conversation")

    if status_filter:
        status_filter = status_filter.lower()

        if status_filter not in valid_statuses:
            return Response(
                {
                    "detail": "status inválido. Use: pending, approved, edited, rejected"
                },
                status=400,
            )

        messages = messages.filter(review_status=valid_statuses[status_filter])

    if channel_filter:
        channel_filter = channel_filter.lower()

        if channel_filter not in valid_channels:
            return Response(
                {
                    "detail": "channel inválido. Use: whatsapp, instagram, facebook, google"
                },
                status=400,
            )

        messages = messages.filter(channel__code=valid_channels[channel_filter])

    if conversation_id:
        try:
            conversation_id = int(conversation_id)
        except ValueError:
            return Response(
                {"detail": "conversation_id deve ser numérico"},
                status=400,
            )

        messages = messages.filter(conversation_id=conversation_id)

    if search:
        messages = messages.filter(
            Q(content__icontains=search)
        )

    messages = messages.order_by("-created_at", "-id")

    paginator = Paginator(messages, page_size)

    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return Response(
            {
                "items": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": paginator.count,
                    "total_pages": paginator.num_pages,
                    "has_next": False,
                    "has_previous": paginator.num_pages > 0,
                },
            }
        )

    data = [
        {
            "id": m.id,
            "conversation_id": m.conversation_id,
            "channel": m.channel.code if m.channel else None,
            "channel_name": m.channel.name if m.channel else None,
            "content": m.content,
            "review_status": m.review_status,
            "created_at": m.created_at,
        }
        for m in page_obj.object_list
    ]

    return Response(
        {
            "items": data,
            "filters": {
                "tenant_id": tenant_id,
                "status": status_filter,
                "channel": channel_filter,
                "conversation_id": conversation_id,
                "search": search,
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": paginator.count,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
    )


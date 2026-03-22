from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Conversation
from .serializers import ConversationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation
from .serializers import ConversationSerializer, ConversationDetailSerializer

class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        tenant_id = self.request.headers.get("X-Tenant-Id")

        if not tenant_id:
            raise ValidationError({"detail": "X-Tenant-Id header is required."})

        queryset = (
            Conversation.objects
            .filter(tenant_id=tenant_id)
            .select_related("customer", "channel", "tenant_channel_account")
            .prefetch_related("customer__identities")
            .order_by("-updated_at")
        )

        return queryset
    
    @action(detail=True, methods=["get"], url_path="detail")
    def detail_view(self, request, pk=None):
        tenant_id = request.headers.get("X-Tenant-Id")

        if not tenant_id:
            raise ValidationError({"detail": "X-Tenant-Id header is required."})

        conversation = (
            Conversation.objects
            .filter(id=pk, tenant_id=tenant_id)
            .select_related("customer", "channel", "tenant_channel_account")
            .prefetch_related("customer__identities")
            .first()
        )

        if not conversation:
            raise ValidationError({"detail": "Conversation not found."})

        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)

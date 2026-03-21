from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Conversation
from .serializers import ConversationSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        tenant_id = self.request.headers.get("X-Tenant-Id")

        if not tenant_id:
            raise ValidationError({"detail": "X-Tenant-Id header is required."})

        queryset = (
            Conversation.objects
            .filter(tenant_id=tenant_id)
            .select_related("customer", "channel")
            .order_by("-updated_at")
        )

        return queryset

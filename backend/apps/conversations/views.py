from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation
from .serializers import ConversationSerializer, ConversationDetailSerializer
from apps.core.utils import get_request_tenant


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer

    def get_tenant(self):
        tenant = get_request_tenant(self.request)

        if not tenant:
            raise PermissionDenied("Usuário sem vínculo ativo com tenant.")

        return tenant

    def get_queryset(self):
        tenant = self.get_tenant()

        queryset = (
            Conversation.objects
            .filter(tenant=tenant)
            .select_related("customer", "channel", "tenant_channel_account")
            .prefetch_related("customer__identities")
            .order_by("-updated_at")
        )

        return queryset

    @action(detail=True, methods=["get"], url_path="detail")
    def detail_view(self, request, pk=None):
        tenant = self.get_tenant()

        conversation = (
            Conversation.objects
            .filter(id=pk, tenant=tenant)
            .select_related("customer", "channel", "tenant_channel_account")
            .prefetch_related("customer__identities")
            .first()
        )

        if not conversation:
            raise ValidationError({"detail": "Conversation not found."})

        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)
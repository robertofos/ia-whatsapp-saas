from rest_framework import serializers
from .models import Conversation


class ConversationSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    channel = serializers.CharField(source="channel.name", read_only=True)
    time = serializers.SerializerMethodField()
    unread = serializers.SerializerMethodField()
    pendingAI = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "name",
            "phone",
            "channel",
            "time",
            "unread",
            "pendingAI",
            "status",
            "updated_at",
        ]

    def _get_identity(self, obj):
        return obj.customer.identities.order_by("id").first()

    def get_name(self, obj):
        identity = self._get_identity(obj)
        if identity and identity.external_display_name:
            return identity.external_display_name
        return f"Customer {obj.customer_id}"

    def get_phone(self, obj):
        identity = self._get_identity(obj)
        if identity and identity.external_user_id:
            return identity.external_user_id
        return ""

    def get_time(self, obj):
        return obj.updated_at.strftime("%H:%M")

    def get_unread(self, obj):
        return 0

    def get_pendingAI(self, obj):
        return False
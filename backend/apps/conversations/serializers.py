from rest_framework import serializers
from .models import Conversation
from apps.messaging.models import Message

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
        return Message.objects.filter(
        conversation=obj,
        review_status="pending",
        ai_generated=True
        ).exists()
    
class ConversationDetailSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    channel = serializers.SerializerMethodField()
    status_tags = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "status",
            "updated_at",
            "customer",
            "channel",
            "status_tags",
            "tags",
            "summary",
            "notes",
        ]

    def _get_identity(self, obj):
        return obj.customer.identities.order_by("id").first()

    def get_customer(self, obj):
        identity = self._get_identity(obj)

        name = f"Customer {obj.customer_id}"
        phone = ""

        if identity:
            if identity.external_display_name:
                name = identity.external_display_name
            if identity.external_user_id:
                phone = identity.external_user_id

        return {
            "id": obj.customer.id,
            "name": name,
            "phone": phone,
            "customer_since": obj.customer.created_at,
        }

    def get_channel(self, obj):
        return {
            "id": obj.channel.id,
            "name": obj.channel.name,
        }

    def get_status_tags(self, obj):
        tags = []

        if obj.status == Conversation.StatusChoices.OPEN:
            tags.append("Em atendimento")
        elif obj.status == Conversation.StatusChoices.CLOSED:
            tags.append("Resolvido")

        return tags

    def get_tags(self, obj):
        return []

    def get_summary(self, obj):
        return ""

    def get_notes(self, obj):
        return ""
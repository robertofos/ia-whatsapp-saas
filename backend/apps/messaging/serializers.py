from rest_framework import serializers
from .models import Message, AIResponseEvaluation


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ("timestamp", "created_at")


class AIResponseEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIResponseEvaluation
        fields = "__all__"
        read_only_fields = ("created_at",)
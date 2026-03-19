from django.contrib import admin
from .models import Message, AIResponseEvaluation


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "sender_type",
        "direction",
        "ai_generated",
        "review_status",
        "created_at",
    )
    list_filter = ("sender_type", "direction", "ai_generated", "review_status")
    search_fields = ("content",)


@admin.register(AIResponseEvaluation)
class AIResponseEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "message",
        "tenant",
        "evaluation_type",
        "created_at",
    )
    list_filter = ("evaluation_type", "tenant")
    search_fields = ("original_response", "final_response")
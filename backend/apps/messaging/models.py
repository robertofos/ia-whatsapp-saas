from django.db import models
from apps.conversations.models import Conversation
from apps.channels.models import Channel
from apps.tenants.models import Tenant
from django.utils import timezone

class Message(models.Model):
    class SenderType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AI = "ai", "AI"
        HUMAN = "human", "Human"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Inbound"
        OUTBOUND = "outbound", "Outbound"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        EDITED = "edited", "Edited"
        REJECTED = "rejected", "Rejected"
    
    class DeliveryStatus(models.TextChoices):
        NOT_SENT = "not_sent", "Not sent"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    external_message_id = models.CharField(max_length=255, blank=True)

    sender_type = models.CharField(
        max_length=20,
        choices=SenderType.choices,
    )

    direction = models.CharField(
        max_length=20,
        choices=Direction.choices,
    )

    content = models.TextField()

    message_type = models.CharField(
        max_length=50,
        default="text",
    )

    ai_generated = models.BooleanField(default=False)

    confidence_score = models.FloatField(null=True, blank=True)

    review_status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    # FIELDS TO SENT MESSAGE
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.NOT_SENT,
    )

    provider_message_id = models.CharField(max_length=255, blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)

    send_error = models.TextField(blank=True)

    raw_payload_json = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} - {self.sender_type}"

class AIResponseEvaluation(models.Model):
    class EvaluationType(models.TextChoices):
        GOOD = "good", "Good"
        BAD = "bad", "Bad"
        EDITED = "edited", "Edited"
        DISCARDED = "discarded", "Discarded"
        TRANSFERRED = "transferred", "Transferred"

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="ai_response_evaluations",
    )

    evaluation_type = models.CharField(
        max_length=20,
        choices=EvaluationType.choices,
    )

    original_response = models.TextField()
    final_response = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation {self.id} - {self.evaluation_type}"
    



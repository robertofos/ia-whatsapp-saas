from django.db import models


class Tenant(models.Model):
    REVIEW_MODE_AUTO = "AUTO"
    REVIEW_MODE_REVIEW = "REVIEW"

    REVIEW_MODE_CHOICES = [
        (REVIEW_MODE_AUTO, "Automático"),
        (REVIEW_MODE_REVIEW, "Revisão"),
    ]
    
    name = models.CharField(max_length=255)
    ai_review_mode = models.CharField(
        max_length=20,
        choices=REVIEW_MODE_CHOICES,
        default=REVIEW_MODE_REVIEW,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

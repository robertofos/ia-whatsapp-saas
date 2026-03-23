from django.db import models
from django.conf import settings

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

class TenantUser(models.Model):
    ROLE_ADMIN = "ADMIN"
    ROLE_AGENT = "AGENT"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_AGENT, "Agent"),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="users",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_links",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_AGENT,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "user")

    def __str__(self):
        return f"{self.user} - {self.tenant} ({self.role})"
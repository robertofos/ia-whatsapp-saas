from django.db import models
from apps.tenants.models import Tenant


class Channel(models.Model):
    class ChannelCode(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        GOOGLE = "google", "Google"

    code = models.CharField(
        max_length=30,
        choices=ChannelCode.choices,
        unique=True,
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TenantChannelAccount(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        PENDING = "pending", "Pending"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="channel_accounts",
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="tenant_accounts",
    )
    external_account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255, blank=True)
    access_token_encrypted = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tenant", "channel", "external_account_id")
        verbose_name = "Tenant Channel Account"
        verbose_name_plural = "Tenant Channel Accounts"

    def __str__(self):
        return f"{self.tenant.name} - {self.channel.name} - {self.external_account_id}"
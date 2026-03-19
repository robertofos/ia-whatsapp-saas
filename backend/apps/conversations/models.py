from django.db import models
from apps.tenants.models import Tenant
from apps.channels.models import Channel, TenantChannelAccount


class Customer(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="customers",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        identity = self.identities.first()
        if identity and identity.external_display_name:
            return f"{identity.external_display_name} ({self.tenant.name})"
        return f"Customer {self.id} ({self.tenant.name})"


class CustomerChannelIdentity(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="identities",
    )
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
    )

    external_user_id = models.CharField(max_length=255)
    external_display_name = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("channel", "external_user_id")

    def __str__(self):
        return f"{self.external_display_name} ({self.channel.name})"

class Conversation(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    tenant_channel_account = models.ForeignKey(
        TenantChannelAccount,
        on_delete=models.CASCADE,
    )

    external_thread_id = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.OPEN,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.channel.name}"
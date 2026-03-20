from django.contrib import admin
from .models import Customer, CustomerChannelIdentity, Conversation


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "phone", "display_name", "created_at")

    def phone(self, obj):
        identity = obj.identities.first()
        return identity.external_user_id if identity else "-"
    phone.short_description = "Telefone"

    def display_name(self, obj):
        identity = obj.identities.first()
        return identity.external_display_name if identity else "-"
    display_name.short_description = "Nome"


@admin.register(CustomerChannelIdentity)
class CustomerChannelIdentityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "channel",
        "external_user_id",
        "external_display_name",
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "customer",
        "customer_phone",
        "channel",
        "status",
        "created_at",
    )

    def customer_phone(self, obj):
        identity = obj.customer.identities.filter(channel=obj.channel).first()
        if not identity or not identity.external_user_id:
            return "-"

        phone = identity.external_user_id
        if phone.startswith("55") and len(phone) >= 12:
            return f"+{phone[:2]} {phone[2:4]} {phone[4:]}"
        return phone
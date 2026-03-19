from django.contrib import admin
from .models import Customer, CustomerChannelIdentity, Conversation


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "created_at")


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
        "channel",
        "status",
        "created_at",
    )
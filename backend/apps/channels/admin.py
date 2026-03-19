from django.contrib import admin
from .models import Channel, TenantChannelAccount


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(TenantChannelAccount)
class TenantChannelAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "channel",
        "external_account_id",
        "account_name",
        "status",
        "created_at",
    )
    search_fields = ("external_account_id", "account_name", "tenant__name")
    list_filter = ("channel", "status")

# Register your models here.

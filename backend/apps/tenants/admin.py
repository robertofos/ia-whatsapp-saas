from django.contrib import admin
from .models import Tenant, TenantUser


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "ai_review_mode", "is_active", "created_at")
    list_filter = ("ai_review_mode", "is_active")
    search_fields = ("name",)

@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "tenant")
    search_fields = ("tenant__name", "user__username", "user__first_name", "user__last_name", "user__email")
from apps.tenants.models import TenantUser


def get_request_tenant(request):
    tenant_link = (
        TenantUser.objects
        .select_related("tenant")
        .filter(
            user=request.user,
            is_active=True,
            tenant__is_active=True,
        )
        .first()
    )

    if not tenant_link:
        return None

    return tenant_link.tenant
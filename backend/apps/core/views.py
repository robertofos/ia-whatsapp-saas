from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenants.models import TenantUser
from .serializers import LoginSerializer


def get_initials(user):
    full_name = f"{user.first_name} {user.last_name}".strip()

    if full_name:
        parts = full_name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return parts[0][:2].upper()

    username = user.username or "US"
    return username[:2].upper()


def get_display_name(user):
    full_name = f"{user.first_name} {user.last_name}".strip()
    return full_name if full_name else user.username


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        tenant_link = (
            TenantUser.objects
            .select_related("tenant", "user")
            .filter(user=user, is_active=True, tenant__is_active=True)
            .first()
        )

        if not tenant_link:
            return Response(
                {"detail": "Usuário sem vínculo ativo com tenant."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "name": get_display_name(user),
                "role": tenant_link.get_role_display(),
                "initials": get_initials(user),
            },
            "tenant": {
                "id": tenant_link.tenant.id,
                "name": tenant_link.tenant.name,
                "ai_review_mode": tenant_link.tenant.ai_review_mode,
            }
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    print(permission_classes)
    def get(self, request):
        tenant_link = (
            TenantUser.objects
            .select_related("tenant", "user")
            .filter(user=request.user, is_active=True, tenant__is_active=True)
            .first()
        )

        if not tenant_link:
            return Response(
                {"detail": "Usuário sem vínculo ativo com tenant."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "name": get_display_name(request.user),
                "role": tenant_link.get_role_display(),
                "initials": get_initials(request.user),
            },
            "tenant": {
                "id": tenant_link.tenant.id,
                "name": tenant_link.tenant.name,
                "ai_review_mode": tenant_link.tenant.ai_review_mode,
            }
        })
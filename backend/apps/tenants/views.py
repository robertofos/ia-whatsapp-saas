from rest_framework.viewsets import ModelViewSet
from .models import Tenant
from .serializers import TenantSerializer


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all().order_by("id")
    serializer_class = TenantSerializer

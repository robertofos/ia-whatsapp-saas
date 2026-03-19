from rest_framework.viewsets import ModelViewSet
from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all().order_by("id")
    serializer_class = MessageSerializer
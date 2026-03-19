from rest_framework.viewsets import ModelViewSet
from .models import Conversation
from .serializers import ConversationSerializer


class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all().order_by("id")
    serializer_class = ConversationSerializer

from rest_framework import serializers
from .models import Customer, CustomerChannelIdentity, Conversation


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class CustomerChannelIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerChannelIdentity
        fields = "__all__"


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"
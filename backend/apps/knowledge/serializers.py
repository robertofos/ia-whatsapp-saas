from rest_framework import serializers


class ProductImportSerializer(serializers.Serializer):
    tenant_id = serializers.IntegerField()
    file = serializers.FileField()


class FAQImportSerializer(serializers.Serializer):
    tenant_id = serializers.IntegerField()
    file = serializers.FileField()
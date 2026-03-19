from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .serializers import ProductImportSerializer, FAQImportSerializer
from .service import import_products_from_excel, import_faqs_from_excel


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def import_products_view(request):
    serializer = ProductImportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = import_products_from_excel(
            tenant_id=serializer.validated_data["tenant_id"],
            file=serializer.validated_data["file"],
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def import_faqs_view(request):
    serializer = FAQImportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        result = import_faqs_from_excel(
            tenant_id=serializer.validated_data["tenant_id"],
            file=serializer.validated_data["file"],
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
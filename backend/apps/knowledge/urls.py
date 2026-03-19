from django.urls import path
from .views import import_products_view, import_faqs_view

urlpatterns = [
    path("knowledge/import/products/", import_products_view, name="import-products"),
    path("knowledge/import/faqs/", import_faqs_view, name="import-faqs"),
]
from django.contrib import admin
from .models import Store, Product, FAQItem


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "tenant", "horario_funcionamento", "taxa_entrega")
    search_fields = ("nome", "tenant__name", "endereco")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "tenant", "categoria", "preco", "disponivel")
    list_filter = ("tenant", "categoria", "disponivel")
    search_fields = ("nome", "descricao")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("id", "pergunta", "tenant", "created_at")
    list_filter = ("tenant",)
    search_fields = ("pergunta", "resposta")
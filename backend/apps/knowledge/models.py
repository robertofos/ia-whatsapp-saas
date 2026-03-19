from django.db import models
from apps.tenants.models import Tenant


class Store(models.Model):
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name="store",
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    horario_funcionamento = models.CharField(max_length=255, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    taxa_entrega = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    formas_pagamento = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.tenant.name})"


class Product(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="products",
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100, blank=True)
    disponivel = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.tenant.name}"


class FAQItem(models.Model):
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="faq_items",
    )
    pergunta = models.CharField(max_length=255)
    resposta = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pergunta} ({self.tenant.name})"

import pandas as pd
from decimal import Decimal, InvalidOperation

from apps.tenants.models import Tenant
from .models import Product, FAQItem


def normalize_bool(value):
    if value is None:
        return False

    value_str = str(value).strip().lower()
    return value_str in {"sim", "true", "1", "yes", "y"}


def import_products_from_excel(tenant_id, file):
    tenant = Tenant.objects.get(id=tenant_id)

    df = pd.read_excel(file)

    expected_columns = {"nome", "descricao", "preco", "categoria", "disponivel"}
    received_columns = set(df.columns.str.strip().str.lower())

    if not expected_columns.issubset(received_columns):
        missing = expected_columns - received_columns
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    df.columns = [col.strip().lower() for col in df.columns]

    created_count = 0

    for _, row in df.iterrows():
        nome = str(row.get("nome", "")).strip()
        descricao = str(row.get("descricao", "")).strip()
        categoria = str(row.get("categoria", "")).strip()
        disponivel = normalize_bool(row.get("disponivel", False))

        preco_raw = row.get("preco")
        if not nome:
            continue

        try:
            preco = Decimal(str(preco_raw))
        except (InvalidOperation, TypeError, ValueError):
            continue

        Product.objects.create(
            tenant=tenant,
            nome=nome,
            descricao=descricao,
            preco=preco,
            categoria=categoria,
            disponivel=disponivel,
        )
        created_count += 1

    return {
        "tenant_id": tenant.id,
        "created_count": created_count,
    }


def import_faqs_from_excel(tenant_id, file):
    tenant = Tenant.objects.get(id=tenant_id)

    df = pd.read_excel(file)

    expected_columns = {"pergunta", "resposta"}
    received_columns = set(df.columns.str.strip().str.lower())

    if not expected_columns.issubset(received_columns):
        missing = expected_columns - received_columns
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    df.columns = [col.strip().lower() for col in df.columns]

    created_count = 0

    for _, row in df.iterrows():
        pergunta = str(row.get("pergunta", "")).strip()
        resposta = str(row.get("resposta", "")).strip()

        if not pergunta or not resposta:
            continue

        FAQItem.objects.create(
            tenant=tenant,
            pergunta=pergunta,
            resposta=resposta,
        )
        created_count += 1

    return {
        "tenant_id": tenant.id,
        "created_count": created_count,
    }
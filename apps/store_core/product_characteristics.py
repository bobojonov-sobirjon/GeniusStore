"""Build grouped product characteristics for API (Whale Store style)."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from django.db.models import Prefetch

from apps.store_core.models import Product, ProductCharacteristic, ProductVariant
from apps.store_core.spec_types import SPEC_TYPE_ORDER, spec_type_label


def characteristics_prefetch() -> Prefetch:
    return Prefetch(
        'characteristics',
        queryset=ProductCharacteristic.objects.order_by('spec_type', 'sort_order', 'title'),
    )


# Backward-compatible alias for serialization imports.
spec_groups_prefetch = characteristics_prefetch


def _characteristics_for_product(product: Product) -> list[ProductCharacteristic]:
    if (
        hasattr(product, '_prefetched_objects_cache')
        and 'characteristics' in getattr(product, '_prefetched_objects_cache', {})
    ):
        return list(product.characteristics.all())
    return list(
        ProductCharacteristic.objects.filter(product_id=product.pk).order_by(
            'spec_type', 'sort_order', 'title',
        )
    )


def _resolve_sim_name(variant: ProductVariant | None, sim_type_id: str | None) -> str | None:
    if variant is None:
        return None
    if sim_type_id:
        for link in variant.sim_type_links.all():
            if str(link.sim_type_id) == sim_type_id and link.sim_type:
                return link.sim_type.name
    st = getattr(variant, 'sim_type', None)
    return st.name if st else None


def _manual_values(text: str) -> list[str]:
    return [line.strip() for line in (text or '').splitlines() if line.strip()]


def _resolve_item_values(
    item: ProductCharacteristic,
    product: Product,
    variant: ProductVariant | None,
    *,
    sim_type_id: str | None = None,
) -> list[str]:
    source = item.variant_source or ''
    if source == ProductCharacteristic.VariantSource.MEMORY:
        memory = getattr(variant, 'memory', None) if variant else None
        return [memory.name] if memory and memory.name else []
    if source == ProductCharacteristic.VariantSource.COLOR:
        color = getattr(variant, 'color', None) if variant else None
        return [color.name] if color and color.name else []
    if source == ProductCharacteristic.VariantSource.SIM:
        name = _resolve_sim_name(variant, sim_type_id)
        return [name] if name else []
    if source == ProductCharacteristic.VariantSource.SERIES:
        val = product.series or product.line or product.title
        return [val] if val else []
    if source == ProductCharacteristic.VariantSource.MODEL:
        pm = getattr(product, 'product_model', None)
        return [pm.name] if pm and pm.name else []
    if source == ProductCharacteristic.VariantSource.CONDITION:
        cond = getattr(product, 'condition', None)
        return [cond.name] if cond and cond.name else []
    if source == ProductCharacteristic.VariantSource.SYSTEM:
        return [product.system] if product.system else []

    return _manual_values(item.value)


def build_characteristic_groups(
    product: Product,
    variant: ProductVariant | None = None,
    *,
    sim_type_id: str | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[ProductCharacteristic]] = defaultdict(list)
    for row in _characteristics_for_product(product):
        grouped[row.spec_type].append(row)

    out: list[dict[str, Any]] = []
    for spec_type in sorted(grouped.keys(), key=lambda t: SPEC_TYPE_ORDER.get(t, 999)):
        rows = grouped[spec_type]
        items_out: list[dict[str, Any]] = []
        for item in rows:
            values = _resolve_item_values(
                item, product, variant, sim_type_id=sim_type_id,
            )
            if not values:
                continue
            items_out.append({
                'id': str(item.id),
                'label': item.title,
                'values': values,
                'source': item.variant_source or 'manual',
                'isVariant': bool(item.variant_source),
            })
        if items_out:
            out.append({
                'id': str(rows[0].id),
                'title': spec_type_label(spec_type),
                'sortOrder': SPEC_TYPE_ORDER.get(spec_type, 999),
                'items': items_out,
            })
    return out

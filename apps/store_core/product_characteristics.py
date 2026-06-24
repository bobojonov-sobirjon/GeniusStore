"""Build grouped product characteristics for API (Whale Store style)."""
from __future__ import annotations

from typing import Any

from django.db.models import Prefetch

from apps.store_core.models import Product, ProductSpecGroup, ProductSpecItem, ProductVariant


def spec_groups_prefetch() -> Prefetch:
    return Prefetch(
        'spec_groups',
        queryset=ProductSpecGroup.objects.prefetch_related(
            Prefetch(
                'items',
                queryset=ProductSpecItem.objects.order_by('sort_order', 'label'),
            ),
        ).order_by('sort_order', 'title'),
    )


def _spec_groups_for_product(product: Product) -> list[ProductSpecGroup]:
    if (
        hasattr(product, '_prefetched_objects_cache')
        and 'spec_groups' in getattr(product, '_prefetched_objects_cache', {})
    ):
        return list(product.spec_groups.all())
    return list(
        ProductSpecGroup.objects.filter(product_id=product.pk)
        .prefetch_related(
            Prefetch(
                'items',
                queryset=ProductSpecItem.objects.order_by('sort_order', 'label'),
            ),
        )
        .order_by('sort_order', 'title')
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


def _resolve_item_values(
    item: ProductSpecItem,
    product: Product,
    variant: ProductVariant | None,
    *,
    sim_type_id: str | None = None,
) -> list[str]:
    source = item.variant_source or ''
    if source == ProductSpecItem.VariantSource.MEMORY:
        memory = getattr(variant, 'memory', None) if variant else None
        return [memory.name] if memory and memory.name else []
    if source == ProductSpecItem.VariantSource.COLOR:
        color = getattr(variant, 'color', None) if variant else None
        return [color.name] if color and color.name else []
    if source == ProductSpecItem.VariantSource.SIM:
        name = _resolve_sim_name(variant, sim_type_id)
        return [name] if name else []
    if source == ProductSpecItem.VariantSource.SERIES:
        val = product.series or product.line or product.title
        return [val] if val else []
    if source == ProductSpecItem.VariantSource.MODEL:
        pm = getattr(product, 'product_model', None)
        return [pm.name] if pm and pm.name else []
    if source == ProductSpecItem.VariantSource.CONDITION:
        cond = getattr(product, 'condition', None)
        return [cond.name] if cond and cond.name else []
    if source == ProductSpecItem.VariantSource.SYSTEM:
        return [product.system] if product.system else []

    raw = item.values if isinstance(item.values, list) else []
    return [str(v).strip() for v in raw if v is not None and str(v).strip()]


def build_characteristic_groups(
    product: Product,
    variant: ProductVariant | None = None,
    *,
    sim_type_id: str | None = None,
) -> list[dict[str, Any]]:
    groups = _spec_groups_for_product(product)
    out: list[dict[str, Any]] = []
    for group in groups:
        items_out: list[dict[str, Any]] = []
        for item in group.items.all():
            values = _resolve_item_values(
                item, product, variant, sim_type_id=sim_type_id,
            )
            if not values:
                continue
            items_out.append({
                'id': str(item.id),
                'label': item.label,
                'values': values,
                'source': item.variant_source or 'manual',
                'isVariant': bool(item.variant_source),
            })
        if items_out:
            out.append({
                'id': str(group.id),
                'title': group.title,
                'sortOrder': group.sort_order,
                'items': items_out,
            })
    return out

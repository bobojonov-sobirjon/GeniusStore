from __future__ import annotations

import math
from typing import Any

from django.db.models import Prefetch

from apps.store_core.models import Product, ProductVariant, ProductVariantSimType


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _sim_link_to_dict(link: ProductVariantSimType) -> dict[str, Any]:
    st = link.sim_type
    return {
        'id': str(link.id),
        'productVariantId': str(link.product_variant_id),
        'simTypeId': str(link.sim_type_id),
        'price': _json_safe(link.price),
        'simType': {'id': str(st.id), 'name': st.name} if st else None,
    }


def variant_to_dict(v: ProductVariant) -> dict[str, Any]:
    sims = [_sim_link_to_dict(link) for link in v.sim_type_links.all()]
    st = v.sim_type
    memory = getattr(v, 'memory', None)
    color = getattr(v, 'color', None)
    return {
        'id': str(v.id),
        'productId': v.product_id,
        'memoryId': v.memory_id,
        'price': _json_safe(v.price),
        'oldPrice': _json_safe(v.old_price),
        'discount': v.discount,
        'isAvailable': v.is_available,
        'description': v.description,
        'colorId': v.color_id,
        'images': v.images if v.images is not None else [],
        'diagonal': v.diagonal,
        'size': v.size,
        'createdAt': v.created_at,
        'updatedAt': v.updated_at,
        'memory': {'id': memory.id, 'name': memory.name} if memory else None,
        'color': {'id': color.id, 'name': color.name, 'hex': color.hex} if color else None,
        'simType': {'id': str(st.id), 'name': st.name} if st else None,
        'simTypeId': str(st.id) if st else None,
        'simTypes': sims,
    }


def _variant_qs():
    return (
        ProductVariant.objects.select_related('memory', 'color', 'sim_type')
        .prefetch_related(
            Prefetch(
                'sim_type_links',
                queryset=ProductVariantSimType.objects.select_related('sim_type'),
            )
        )
    )


def product_to_dict(p: Product, variants: list[ProductVariant] | None = None) -> dict[str, Any]:
    if variants is None:
        variants = list(_variant_qs().filter(product=p))
    brand = getattr(p, 'brand', None)
    category = getattr(p, 'category', None)
    condition = getattr(p, 'condition', None) if p.condition_id else None
    model = getattr(p, 'product_model', None) if p.product_model_id else None
    return {
        'id': p.id,
        'title': p.title,
        'rating': _json_safe(p.rating),
        'isAvailable': p.is_available,
        'isNew': p.is_new,
        'isHit': p.is_hit,
        'isBt': p.is_bt,
        'article': p.article,
        'description': p.description,
        'slug': p.slug,
        'brandId': p.brand_id,
        'categoryId': p.category_id,
        'conditionId': str(p.condition_id) if p.condition_id else None,
        'modelId': p.product_model_id,
        'type': p.type,
        'class': p.product_class,
        'line': p.line,
        'series': p.series,
        'system': p.system,
        'version': p.version,
        'diagonal': p.diagonal,
        'size': p.size,
        'screenType': p.screen_type,
        'resolution': p.resolution,
        'refreshRate': p.refresh_rate,
        'density': p.density,
        'brightness': p.brightness,
        'glass': p.glass,
        'aod': p.aod,
        'createdAt': p.created_at,
        'updatedAt': p.updated_at,
        'brand': {'id': brand.id, 'name': brand.name} if brand else None,
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
        } if category else None,
        'condition': {'id': str(condition.id), 'name': condition.name} if condition else None,
        'model': {'id': model.id, 'name': model.name} if model else None,
        'variants': [variant_to_dict(v) for v in variants],
    }

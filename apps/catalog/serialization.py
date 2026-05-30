from __future__ import annotations

from typing import Any

from django.db.models import Prefetch

from apps.store_core.models import Product, ProductVariant, ProductVariantSimType


def _sim_link_to_dict(link: ProductVariantSimType) -> dict[str, Any]:
    return {
        'id': str(link.id),
        'productVariantId': str(link.product_variant_id),
        'simTypeId': str(link.sim_type_id),
        'price': link.price,
        'simType': {'id': str(link.sim_type.id), 'name': link.sim_type.name},
    }


def variant_to_dict(v: ProductVariant) -> dict[str, Any]:
    sims = [_sim_link_to_dict(l) for l in v.sim_type_links.all()]
    st = v.sim_type
    return {
        'id': str(v.id),
        'productId': v.product_id,
        'memoryId': v.memory_id,
        'price': v.price,
        'oldPrice': v.old_price,
        'discount': v.discount,
        'isAvailable': v.is_available,
        'description': v.description,
        'colorId': v.color_id,
        'images': v.images,
        'diagonal': v.diagonal,
        'size': v.size,
        'createdAt': v.created_at,
        'updatedAt': v.updated_at,
        'memory': {'id': v.memory_id, 'name': v.memory.name},
        'color': {'id': v.color_id, 'name': v.color.name, 'hex': v.color.hex},
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
    return {
        'id': p.id,
        'title': p.title,
        'rating': p.rating,
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
        'brand': {'id': p.brand.id, 'name': p.brand.name},
        'category': {'id': p.category.id, 'name': p.category.name, 'slug': p.category.slug},
        'condition': {'id': str(p.condition.id), 'name': p.condition.name} if p.condition_id else None,
        'model': {'id': p.product_model.id, 'name': p.product_model.name} if p.product_model_id else None,
        'variants': [variant_to_dict(v) for v in variants],
    }

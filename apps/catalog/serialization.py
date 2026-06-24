from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from django.db.models import Prefetch

from apps.common.media_urls import media_url, media_url_images
from apps.store_core.category_specs import build_specifications, spec_field_names_for_category
from apps.store_core.product_characteristics import build_characteristic_groups, spec_groups_prefetch
from apps.store_core.models import Product, ProductImage, ProductVariant, ProductVariantSimType


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _serialize_gallery_rows(rows: list[ProductImage], request=None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for img in rows:
        url = media_url(img.image, request)
        if not url:
            continue
        color = getattr(img, 'color', None)
        out.append({
            'id': str(img.id),
            'url': url,
            'alt': img.alt or '',
            'isPrimary': img.is_primary,
            'sortOrder': img.sort_order,
            'colorId': img.color_id,
            'color': {
                'id': color.id,
                'name': color.name,
                'hex': color.hex,
            } if color else None,
        })
    return out


def _product_image_rows(product: Product) -> list[ProductImage]:
    if (
        hasattr(product, '_prefetched_objects_cache')
        and 'product_images' in getattr(product, '_prefetched_objects_cache', {})
    ):
        return list(product.product_images.all())
    return list(product.product_images.select_related('color').order_by('sort_order', '-created_at'))


def product_gallery_images(product: Product, request=None) -> list[dict[str, Any]]:
    """All product gallery images (admin ProductImage tab)."""
    return _serialize_gallery_rows(_product_image_rows(product), request)


def variant_gallery_images(
    variant: ProductVariant,
    product: Product | None = None,
    request=None,
) -> list[Any]:
    """
    Images for a variant: by color → variant JSON → shared (no color) → legacy all.
    """
    prod = product or getattr(variant, 'product', None)
    if prod is None:
        return media_url_images(variant.images, request)

    rows = _product_image_rows(prod)
    color_id = variant.color_id

    if color_id and rows:
        by_color = [r for r in rows if r.color_id == color_id]
        if by_color:
            return _serialize_gallery_rows(by_color, request)

    variant_json = media_url_images(variant.images, request)
    if variant_json:
        return variant_json

    if rows:
        shared = [r for r in rows if r.color_id is None]
        if shared:
            return _serialize_gallery_rows(shared, request)
        if not any(r.color_id for r in rows):
            return _serialize_gallery_rows(rows, request)

    return []


def _resolve_variant_images(
    v: ProductVariant,
    *,
    product: Product | None = None,
    request=None,
) -> list[Any]:
    return variant_gallery_images(v, product=product, request=request)


def _sim_link_to_dict(link: ProductVariantSimType) -> dict[str, Any]:
    st = link.sim_type
    return {
        'id': str(link.id),
        'productVariantId': str(link.product_variant_id),
        'simTypeId': str(link.sim_type_id),
        'price': _json_safe(link.price),
        'simType': {'id': str(st.id), 'name': st.name} if st else None,
    }


def variant_to_dict(
    v: ProductVariant,
    *,
    product: Product | None = None,
    request=None,
) -> dict[str, Any]:
    sims = [_sim_link_to_dict(link) for link in v.sim_type_links.all()]
    st = v.sim_type
    memory = getattr(v, 'memory', None)
    color = getattr(v, 'color', None)
    prod = product or getattr(v, 'product', None)
    images = _resolve_variant_images(v, product=prod, request=request)
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
        'images': images,
        'diagonal': v.diagonal,
        'size': v.size,
        'createdAt': v.created_at,
        'updatedAt': v.updated_at,
        'memory': {'id': memory.id, 'name': memory.name} if memory else None,
        'color': {
            'id': color.id,
            'name': color.name,
            'hex': color.hex or '#cccccc',
        } if color else None,
        'simType': {'id': str(st.id), 'name': st.name} if st else None,
        'simTypeId': str(st.id) if st else None,
        'simTypes': sims,
        'specifications': build_specifications(prod, v) if prod else [],
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


def product_list_prefetch() -> list[Prefetch]:
    return [
        Prefetch('variants', queryset=_variant_qs()),
        Prefetch(
            'product_images',
            queryset=ProductImage.objects.select_related('color').order_by('sort_order', '-created_at'),
        ),
        spec_groups_prefetch(),
    ]


def _build_color_options(
    variants: list[ProductVariant],
    product: Product,
    request=None,
) -> list[dict[str, Any]]:
    """Unique colors with gallery + memory/price variants (Whale Store color picker)."""
    by_color: dict[int, dict[str, Any]] = {}
    for v in variants:
        if not v.color_id:
            continue
        color = v.color
        if v.color_id not in by_color:
            sample = v
            by_color[v.color_id] = {
                'id': color.id,
                'name': color.name,
                'hex': color.hex or '#cccccc',
                'images': variant_gallery_images(sample, product=product, request=request),
                'memories': [],
            }
        memory = getattr(v, 'memory', None)
        by_color[v.color_id]['memories'].append({
            'variantId': str(v.id),
            'memoryId': v.memory_id,
            'name': memory.name if memory else None,
            'price': _json_safe(v.price),
            'oldPrice': _json_safe(v.old_price),
            'discount': v.discount,
            'isAvailable': v.is_available,
        })
    return list(by_color.values())


@dataclass(frozen=True)
class ProductSelection:
    color_id: int | None = None
    memory_id: int | None = None
    sim_type_id: str | None = None

    @property
    def is_filtered(self) -> bool:
        return any(v is not None for v in (self.color_id, self.memory_id, self.sim_type_id))


def parse_product_selection(query_params) -> ProductSelection:
    def _int_param(key: str) -> int | None:
        raw = query_params.get(key)
        if raw in (None, ''):
            return None
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'Некорректный параметр {key}: ожидается число') from exc

    sim_raw = query_params.get('simTypeId')
    sim_type_id = None if sim_raw in (None, '') else str(sim_raw).strip()
    return ProductSelection(
        color_id=_int_param('colorId'),
        memory_id=_int_param('memoryId'),
        sim_type_id=sim_type_id or None,
    )


def resolve_selected_variant(
    variants: list[ProductVariant],
    selection: ProductSelection,
) -> ProductVariant | None:
    if not variants:
        return None
    pool = variants
    if selection.color_id is not None:
        pool = [v for v in pool if v.color_id == selection.color_id]
    if selection.memory_id is not None:
        pool = [v for v in pool if v.memory_id == selection.memory_id]
    if not pool:
        return None
    return pool[0]


def _apply_sim_type_price(variant_data: dict[str, Any], sim_type_id: str) -> dict[str, Any]:
    for link in variant_data.get('simTypes') or []:
        if str(link.get('simTypeId')) == sim_type_id:
            variant_data = dict(variant_data)
            variant_data['price'] = link.get('price')
            sim = link.get('simType')
            if sim:
                variant_data['simType'] = sim
                variant_data['simTypeId'] = sim.get('id')
            return variant_data
    return variant_data


def apply_product_selection(
    data: dict[str, Any],
    product: Product,
    variants: list[ProductVariant],
    selection: ProductSelection,
    *,
    request=None,
) -> dict[str, Any]:
    """Apply color/memory/sim filters and expose selectedVariant for the product card."""
    if selection.is_filtered:
        selected = resolve_selected_variant(variants, selection)
        if selected is None:
            parts = []
            if selection.color_id is not None:
                parts.append(f'colorId={selection.color_id}')
            if selection.memory_id is not None:
                parts.append(f'memoryId={selection.memory_id}')
            raise ValueError('Вариант не найден: ' + ', '.join(parts))
    else:
        selected = variants[0] if variants else None

    out = dict(data)
    out['selection'] = {
        'colorId': selection.color_id,
        'memoryId': selection.memory_id,
        'simTypeId': selection.sim_type_id,
    }

    if not selected:
        out['selectedVariant'] = None
        return out

    variant_data = variant_to_dict(selected, product=product, request=request)
    if selection.sim_type_id:
        variant_data = _apply_sim_type_price(variant_data, selection.sim_type_id)

    out['selectedVariant'] = variant_data
    out['images'] = variant_data['images']
    out['specifications'] = variant_data['specifications']
    out['characteristicGroups'] = build_characteristic_groups(
        product,
        selected,
        sim_type_id=selection.sim_type_id,
    )
    return out


def product_to_dict(
    p: Product,
    variants: list[ProductVariant] | None = None,
    request=None,
    selection: ProductSelection | None = None,
) -> dict[str, Any]:
    if variants is None:
        variants = list(_variant_qs().filter(product=p))
    default_variant = variants[0] if variants else None
    gallery = (
        variant_gallery_images(default_variant, product=p, request=request)
        if default_variant
        else product_gallery_images(p, request)
    )
    brand = getattr(p, 'brand', None)
    category = getattr(p, 'category', None)
    condition = getattr(p, 'condition', None) if p.condition_id else None
    model = getattr(p, 'product_model', None) if p.product_model_id else None
    category_slug = category.slug if category else None
    base = {
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
        'brand': {
            'id': brand.id,
            'name': brand.name,
            'image': media_url(brand.image, request),
        } if brand else None,
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
        } if category else None,
        'condition': {'id': str(condition.id), 'name': condition.name} if condition else None,
        'model': {'id': model.id, 'name': model.name} if model else None,
        'images': gallery,
        'colors': _build_color_options(variants, p, request=request),
        'specFields': list(spec_field_names_for_category(category_slug)),
        'specifications': build_specifications(p, default_variant),
        'characteristicGroups': build_characteristic_groups(p, default_variant),
        'variants': [
            variant_to_dict(v, product=p, request=request) for v in variants
        ],
    }
    if selection is not None:
        return apply_product_selection(base, p, variants, selection, request=request)
    return base

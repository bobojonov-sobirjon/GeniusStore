from __future__ import annotations

import json
import re
import uuid
from typing import Any

from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone

from apps.catalog.serialization import _variant_qs, product_to_dict, variant_to_dict
from apps.common.file_storage import delete_media_relative, save_upload_file
from apps.common.media_urls import media_url
from apps.common.slugify_store import generate_slug
from apps.store_core.models import (
    Color,
    Memory,
    Product,
    ProductVariant,
    ProductVariantSimType,
)


def _truthy(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ('true', '1', 'yes')


def _parse_variants(raw: Any) -> list[dict]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
    return []


def _collect_variant_files(files) -> dict[int, dict[int, Any]]:
    """fieldname `variant_{i}_image_{j}` -> map[i][j] = file (Django MultiValueDict)."""
    out: dict[int, dict[int, Any]] = {}
    if not files:
        return out
    for key in files.keys():
        m = re.match(r'variant_(\d+)_image_(\d+)', key)
        if not m:
            continue
        i, j = int(m.group(1)), int(m.group(2))
        for f in files.getlist(key):
            out.setdefault(i, {})[j] = f
    return out


def _images_from_files(variant_files: dict[int, Any] | None) -> list[dict]:
    if not variant_files:
        return []
    images = []
    for j in sorted(variant_files.keys()):
        f = variant_files[j]
        if f:
            rel = save_upload_file('image', f)
            images.append({'id': str(uuid.uuid4()), 'path': rel, 'alt': 'Variant image'})
    return images


@transaction.atomic
def create_product(data: dict, files) -> Product:
    variants_raw = _parse_variants(data.get('variants'))
    vmap = _collect_variant_files(files)

    slug_base = generate_slug(data['title'])
    slug = slug_base
    n = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f'{slug_base}-{n}'
        n += 1

    p = Product.objects.create(
        title=data['title'],
        slug=slug,
        rating=float(data['rating']) if data.get('rating') not in (None, '') else None,
        is_new=_truthy(data.get('isNew')),
        is_hit=_truthy(data.get('isHit')),
        is_bt=_truthy(data.get('isBt')),
        article=data.get('article') or None,
        description=data.get('description') or None,
        brand_id=int(data['brandId']),
        category_id=int(data['categoryId']),
        condition_id=data.get('conditionId') or None,
        product_model_id=int(data['modelId']) if data.get('modelId') not in (None, '') else None,
        type=data.get('type') or None,
        product_class=data.get('class') or None,
        line=data.get('line') or None,
        series=data.get('series') or None,
        system=data.get('system') or None,
        version=data.get('version') or None,
        diagonal=data.get('diagonal') or None,
        size=data.get('size') or None,
        screen_type=data.get('screenType') or None,
        resolution=data.get('resolution') or None,
        refresh_rate=data.get('refreshRate') or None,
        density=data.get('density') or None,
        brightness=data.get('brightness') or None,
        glass=data.get('glass') or None,
        aod=data.get('aod') or None,
    )

    for index, variant in enumerate(variants_raw):
        imgs = _images_from_files(vmap.get(index))
        pv = ProductVariant.objects.create(
            id=str(uuid.uuid4()),
            product=p,
            memory_id=int(variant['memoryId']),
            price=float(variant['price']),
            old_price=float(variant['oldPrice']) if variant.get('oldPrice') not in (None, '') else None,
            discount=int(variant['discount']) if variant.get('discount') not in (None, '') else None,
            is_available=_truthy(variant.get('isAvailable', True)),
            color_id=int(variant['colorId']),
            images=imgs or None,
            diagonal=variant.get('diagonal') or None,
            size=variant.get('size') or None,
            description=variant.get('description') or None,
        )
        for st in variant.get('simTypes') or []:
            ProductVariantSimType.objects.create(
                id=str(uuid.uuid4()),
                product_variant=pv,
                sim_type_id=str(st['simTypeId']),
                price=float(st['price']) if st.get('price') not in (None, '') else float(variant['price']),
            )
    p.refresh_from_db()
    return Product.objects.select_related('brand', 'category', 'condition', 'product_model').get(pk=p.pk)


@transaction.atomic
def update_product(pid: int, data: dict, files) -> Product:
    p = Product.objects.select_for_update().get(pk=pid)
    if data.get('title'):
        p.title = data['title']
        p.slug = generate_slug(data['title'])
    if data.get('description') is not None:
        p.description = data.get('description')
    if data.get('article') is not None:
        p.article = data.get('article')
    if data.get('rating') not in (None, ''):
        p.rating = float(data['rating'])
    if data.get('isNew') is not None:
        p.is_new = _truthy(data.get('isNew'))
    if data.get('isHit') is not None:
        p.is_hit = _truthy(data.get('isHit'))
    if data.get('isBt') is not None:
        p.is_bt = _truthy(data.get('isBt'))
    if data.get('brandId'):
        p.brand_id = int(data['brandId'])
    if data.get('categoryId'):
        p.category_id = int(data['categoryId'])
    if 'conditionId' in data:
        p.condition_id = data.get('conditionId') or None
    if 'modelId' in data:
        p.product_model_id = int(data['modelId']) if data.get('modelId') not in (None, '') else None
    for fld, key in [
        ('type', 'type'),
        ('product_class', 'class'),
        ('line', 'line'),
        ('series', 'series'),
        ('system', 'system'),
        ('version', 'version'),
        ('diagonal', 'diagonal'),
        ('size', 'size'),
        ('screen_type', 'screenType'),
        ('resolution', 'resolution'),
        ('refresh_rate', 'refreshRate'),
        ('density', 'density'),
        ('brightness', 'brightness'),
        ('glass', 'glass'),
        ('aod', 'aod'),
    ]:
        if key in data:
            setattr(p, fld, data.get(key))
    p.updated_at = timezone.now()
    p.save()

    variants_raw = _parse_variants(data.get('variants'))
    vmap = _collect_variant_files(files)
    for index, variant in enumerate(variants_raw):
        imgs_existing = variant.get('images') or []
        new_files = vmap.get(index) or {}
        for fi in sorted(new_files.keys()):
            f = new_files[fi]
            if f:
                rel = save_upload_file('image', f)
                imgs_existing.append({'id': str(uuid.uuid4()), 'path': rel, 'alt': 'Variant image'})
        vid = variant.get('id')
        if vid:
            pv = ProductVariant.objects.select_for_update().get(pk=str(vid))
            pv.memory_id = int(variant['memoryId'])
            pv.price = float(variant['price'])
            pv.old_price = float(variant['oldPrice']) if variant.get('oldPrice') not in (None, '') else None
            pv.discount = int(variant['discount']) if variant.get('discount') not in (None, '') else None
            pv.is_available = _truthy(variant.get('isAvailable', True))
            pv.color_id = int(variant['colorId'])
            pv.images = imgs_existing or None
            pv.diagonal = variant.get('diagonal') or None
            pv.size = variant.get('size') or None
            pv.description = variant.get('description') or None
            pv.updated_at = timezone.now()
            pv.save()
            if 'simTypes' in variant:
                ProductVariantSimType.objects.filter(product_variant=pv).delete()
                for st in variant.get('simTypes') or []:
                    ProductVariantSimType.objects.create(
                        id=str(uuid.uuid4()),
                        product_variant=pv,
                        sim_type_id=str(st['simTypeId']),
                        price=float(st['price']) if st.get('price') not in (None, '') else float(variant['price']),
                    )
        else:
            pv = ProductVariant.objects.create(
                id=str(uuid.uuid4()),
                product=p,
                memory_id=int(variant['memoryId']),
                price=float(variant['price']),
                old_price=float(variant['oldPrice']) if variant.get('oldPrice') not in (None, '') else None,
                discount=int(variant['discount']) if variant.get('discount') not in (None, '') else None,
                is_available=_truthy(variant.get('isAvailable', True)),
                color_id=int(variant['colorId']),
                images=imgs_existing or None,
                diagonal=variant.get('diagonal') or None,
                size=variant.get('size') or None,
            )
            for st in variant.get('simTypes') or []:
                ProductVariantSimType.objects.create(
                    id=str(uuid.uuid4()),
                    product_variant=pv,
                    sim_type_id=str(st['simTypeId']),
                    price=float(st['price']) if st.get('price') not in (None, '') else float(variant['price']),
                )
    return Product.objects.select_related('brand', 'category', 'condition', 'product_model').get(pk=p.pk)


def delete_product(pid: int) -> None:
    ProductVariant.objects.filter(product_id=pid).delete()
    Product.objects.filter(pk=pid).delete()


def get_product(pid: int) -> dict | None:
    p = (
        Product.objects.select_related('brand', 'category', 'condition', 'product_model')
        .filter(pk=pid)
        .first()
    )
    if not p:
        return None
    return product_to_dict(p)


def get_product_by_slug(slug: str) -> dict | None:
    p = (
        Product.objects.select_related('brand', 'category', 'condition', 'product_model')
        .filter(slug=slug)
        .first()
    )
    if not p:
        return None
    return product_to_dict(p)


def list_products_page(page: int, limit: int) -> dict:
    page = max(1, int(page))
    limit = max(1, min(int(limit), 100))
    base_qs = Product.objects.all()
    total = base_qs.count()
    qs = (
        base_qs.select_related('brand', 'category', 'condition', 'product_model')
        .prefetch_related(Prefetch('variants', queryset=_variant_qs()))
        .order_by('-created_at')[(page - 1) * limit : page * limit]
    )
    data = [product_to_dict(p, variants=list(p.variants.all())) for p in qs]
    return {'data': data, 'count': total, 'page': page, 'limit': limit}


def list_products_category_id(page: int, limit: int, category_id: int) -> dict:
    page = max(1, int(page))
    limit = max(1, min(int(limit), 100))
    base_qs = Product.objects.filter(category_id=category_id)
    cnt = base_qs.count()
    qs = (
        base_qs.select_related('brand', 'category', 'condition', 'product_model')
        .prefetch_related(Prefetch('variants', queryset=_variant_qs()))
        .order_by('-created_at')[(page - 1) * limit : page * limit]
    )
    return {
        'data': [product_to_dict(p, variants=list(p.variants.all())) for p in qs],
        'count': cnt,
        'page': page,
        'limit': limit,
    }


def list_products_category_slug(page: int, limit: int, slug: str) -> dict:
    from apps.store_core.models import Category

    page = max(1, int(page))
    limit = max(1, min(int(limit), 100))
    cat = Category.objects.filter(slug=slug).first()
    base_qs = Product.objects.filter(category__slug=slug)
    cnt = base_qs.count()
    qs = (
        base_qs.select_related('brand', 'category', 'condition', 'product_model')
        .prefetch_related(Prefetch('variants', queryset=_variant_qs()))
        .order_by('-created_at')[(page - 1) * limit : page * limit]
    )
    cat_out = (
        {'id': cat.id, 'name': cat.name, 'slug': cat.slug, 'icon': media_url(cat.icon), 'createdAt': cat.created_at}
        if cat
        else None
    )
    return {
        'data': [product_to_dict(p, variants=list(p.variants.all())) for p in qs],
        'category': cat_out,
        'count': cnt,
        'page': page,
        'limit': limit,
    }


def search_products(q: str) -> list[dict]:
    q = (q or '').strip()
    if not q:
        return []
    qs = (
        Product.objects.select_related('brand', 'category', 'condition', 'product_model')
        .filter(Q(title__icontains=q) | Q(description__icontains=q))
        .order_by('-created_at')
    )
    return [product_to_dict(p) for p in qs]


@transaction.atomic
def update_variant(vid: str, dto: dict) -> dict:
    pv = ProductVariant.objects.select_for_update().get(pk=vid)
    if 'price' in dto and dto['price'] is not None:
        pv.price = float(dto['price'])
    if 'oldPrice' in dto:
        pv.old_price = None if dto['oldPrice'] is None else float(dto['oldPrice'])
    if 'discount' in dto:
        pv.discount = None if dto['discount'] is None else int(dto['discount'])
    if 'isAvailable' in dto:
        pv.is_available = bool(dto['isAvailable'])
    if 'colorId' in dto:
        cid = dto['colorId']
        if cid is None:
            raise ValueError('Color not found')
        if not Color.objects.filter(pk=cid).exists():
            raise ValueError('Color not found')
        pv.color_id = int(cid)
    if 'diagonal' in dto:
        pv.diagonal = dto.get('diagonal')
    if 'size' in dto:
        pv.size = dto.get('size')
    if 'images' in dto:
        pv.images = dto.get('images')
    pv.updated_at = timezone.now()
    pv.save()
    if 'simTypes' in dto:
        ProductVariantSimType.objects.filter(product_variant=pv).delete()
        for st in dto.get('simTypes') or []:
            price = st.get('price')
            if price is None or price == '':
                price = pv.price
            ProductVariantSimType.objects.create(
                id=str(uuid.uuid4()),
                product_variant=pv,
                sim_type_id=str(st['simTypeId']),
                price=float(price),
            )
    pv = (
        ProductVariant.objects.select_related('product', 'memory', 'color', 'sim_type')
        .prefetch_related('sim_type_links__sim_type')
        .get(pk=vid)
    )
    return variant_to_dict(pv)


def delete_variant(vid: str) -> None:
    ProductVariant.objects.filter(pk=vid).delete()


def remove_variant_image(vid: str, image_id: str) -> dict:
    pv = ProductVariant.objects.get(pk=vid)
    images = list(pv.images or [])
    found = next((i for i in images if i.get('id') == image_id), None)
    if not found:
        raise LookupError('Image not found')
    images = [i for i in images if i.get('id') != image_id]
    pv.images = images or None
    pv.save()
    return {'success': True, 'message': 'Image removed successfully', 'variantId': vid, 'imageId': image_id, 'remainingImages': len(images)}

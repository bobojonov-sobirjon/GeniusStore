"""Duplicate a product with images, variants, SIM prices and characteristics."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import transaction
from apps.common.file_storage import IMAGE_UPLOAD_TO
from apps.common.slugify_store import generate_slug
from apps.store_core.models import (
    Product,
    ProductCharacteristic,
    ProductImage,
    ProductVariant,
    ProductVariantSimType,
)

_PRODUCT_COPY_FIELDS = (
    'rating',
    'is_available',
    'is_new',
    'is_hit',
    'is_bt',
    'article',
    'description',
    'brand_id',
    'category_id',
    'condition_id',
    'product_model_id',
    'type',
    'product_class',
    'line',
    'series',
    'system',
    'version',
    'diagonal',
    'size',
    'screen_type',
    'resolution',
    'refresh_rate',
    'density',
    'brightness',
    'glass',
    'aod',
)


def _unique_slug(base: str) -> str:
    slug = base or 'product'
    n = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


def _copy_media_file(relative_path: str | None) -> str | None:
    """Copy a media file under MEDIA_ROOT; return new relative path (or original if missing)."""
    if not relative_path:
        return relative_path
    rel = str(relative_path).lstrip('/')
    src = Path(settings.MEDIA_ROOT) / rel
    if not src.is_file():
        return rel
    ext = src.suffix.lstrip('.') or 'bin'
    new_rel = f'{IMAGE_UPLOAD_TO}{uuid.uuid4()}.{ext}'
    dest = Path(settings.MEDIA_ROOT) / new_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return new_rel


def _copy_variant_images_json(images: Any) -> list | None:
    if not images:
        return None
    if not isinstance(images, list):
        return images
    out = []
    for item in images:
        if not isinstance(item, dict):
            out.append(item)
            continue
        row = dict(item)
        row['id'] = str(uuid.uuid4())
        if row.get('path'):
            row['path'] = _copy_media_file(row['path'])
        out.append(row)
    return out or None


@transaction.atomic
def duplicate_product(source: Product) -> Product:
    """
    Create a full copy of ``source``:
    product fields, gallery images, variants (+ SIM links), characteristics.
    Title gets « (копия)», slug is unique.
    """
    title = f'{source.title} (копия)'
    slug = _unique_slug(generate_slug(title) or f'{source.slug}-copy')

    kwargs: dict[str, Any] = {field: getattr(source, field) for field in _PRODUCT_COPY_FIELDS}
    copy = Product.objects.create(
        title=title,
        slug=slug,
        **kwargs,
    )

    for img in source.product_images.all().order_by('sort_order', '-created_at'):
        ProductImage.objects.create(
            id=uuid.uuid4(),
            product=copy,
            image=_copy_media_file(img.image.name if img.image else None) or '',
            alt=img.alt,
            sort_order=img.sort_order,
            is_primary=img.is_primary,
            color_id=img.color_id,
        )

    for char in source.characteristics.all().order_by('spec_type', 'sort_order', 'title'):
        ProductCharacteristic.objects.create(
            id=uuid.uuid4(),
            product=copy,
            spec_type=char.spec_type,
            title=char.title,
            value=char.value,
            sort_order=char.sort_order,
        )

    variants = (
        source.variants.select_related('memory', 'color', 'sim_type')
        .prefetch_related('sim_type_links')
        .order_by('price', 'id')
    )
    for v in variants:
        new_v = ProductVariant.objects.create(
            id=str(uuid.uuid4()),
            product=copy,
            memory_id=v.memory_id,
            price=v.price,
            old_price=v.old_price,
            discount=v.discount,
            is_available=v.is_available,
            description=v.description,
            color_id=v.color_id,
            images=_copy_variant_images_json(v.images),
            diagonal=v.diagonal,
            size=v.size,
            sim_type_id=v.sim_type_id,
        )
        for link in v.sim_type_links.all():
            ProductVariantSimType.objects.create(
                id=str(uuid.uuid4()),
                product_variant=new_v,
                sim_type_id=link.sim_type_id,
                price=link.price,
            )

    return copy

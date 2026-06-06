from __future__ import annotations

from typing import Any

from django.db.models import Q

from apps.catalog.serialization import product_gallery_images, product_list_prefetch, product_to_dict, variant_to_dict
from apps.common.media_urls import media_url
from apps.store_core.models import Category, Product, ProductModel, ProductVariant
from apps.storefront.models import CartItem, Favorite, Review, SiteSettings

DEFAULT_ADVANTAGES = [
    {
        'title': 'Гарантия магазина',
        'description': '365 дней гарантии на всю технику',
        'icon': 'shield',
    },
    {
        'title': 'Выездной сервис',
        'description': 'Специалисты приедут в удобное место',
        'icon': 'service',
    },
    {
        'title': 'Быстрая доставка',
        'description': 'Доставка по СПб в день заказа или самовывоз',
        'icon': 'delivery',
    },
    {
        'title': 'Trade-in техники',
        'description': 'Обменяйте старое устройство на новое',
        'icon': 'tradein',
    },
]


def _first_image(images) -> str | None:
    if not images or not isinstance(images, list):
        return None
    first = images[0]
    if isinstance(first, str):
        return first
    if isinstance(first, dict):
        return first.get('url') or first.get('path') or first.get('src')
    return None


def variant_card(v: ProductVariant) -> dict[str, Any]:
    p = v.product
    return {
        'variantId': str(v.id),
        'productId': p.id,
        'title': p.title,
        'slug': p.slug,
        'price': v.price,
        'oldPrice': v.old_price,
        'discount': v.discount,
        'isAvailable': v.is_available,
        'image': media_url(_first_image(product_gallery_images(p) or v.images)),
        'memory': {'id': v.memory_id, 'name': v.memory.name},
        'color': {'id': v.color_id, 'name': v.color.name, 'hex': v.color.hex},
        'brand': {'id': p.brand_id, 'name': p.brand.name},
        'category': {'id': p.category_id, 'name': p.category.name, 'slug': p.category.slug},
    }


def _variants_qs():
    return ProductVariant.objects.select_related(
        'memory', 'color', 'sim_type', 'product', 'product__brand', 'product__category'
    )


def _load_variants(variant_ids: list[str]) -> dict[str, ProductVariant]:
    if not variant_ids:
        return {}
    rows = _variants_qs().filter(pk__in=variant_ids)
    return {str(v.id): v for v in rows}


def list_favorites(user_id: str) -> list[dict]:
    ids = list(
        Favorite.objects.filter(user_id=user_id).order_by('-created_at').values_list('variant_id', flat=True)
    )
    by_id = _load_variants([str(i) for i in ids])
    return [variant_card(by_id[str(vid)]) for vid in ids if str(vid) in by_id]


def add_favorite(user_id: str, variant_id: str) -> dict:
    if not ProductVariant.objects.filter(pk=variant_id).exists():
        raise LookupError('Variant not found')
    Favorite.objects.get_or_create(user_id=user_id, variant_id=variant_id)
    v = _variants_qs().get(pk=variant_id)
    return variant_card(v)


def remove_favorite(user_id: str, variant_id: str) -> None:
    Favorite.objects.filter(user_id=user_id, variant_id=variant_id).delete()


def list_cart(user_id: str) -> dict[str, Any]:
    items = list(CartItem.objects.filter(user_id=user_id).order_by('-updated_at'))
    by_id = _load_variants([str(i.variant_id) for i in items])
    rows = []
    total = 0
    for item in items:
        v = by_id.get(str(item.variant_id))
        if not v:
            continue
        line_sum = int(v.price * item.quantity)
        total += line_sum
        rows.append(
            {
                'id': str(item.id),
                'variantId': str(item.variant_id),
                'quantity': item.quantity,
                'lineTotal': line_sum,
                'product': variant_card(v),
            }
        )
    return {'items': rows, 'totalPrice': total, 'count': len(rows)}


def add_cart_item(user_id: str, variant_id: str, quantity: int = 1) -> dict:
    if quantity < 1:
        raise ValueError('quantity must be >= 1')
    if not ProductVariant.objects.filter(pk=variant_id).exists():
        raise LookupError('Variant not found')
    item, created = CartItem.objects.get_or_create(
        user_id=user_id,
        variant_id=variant_id,
        defaults={'quantity': quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=['quantity', 'updated_at'])
    return list_cart(user_id)


def update_cart_quantity(user_id: str, variant_id: str, quantity: int) -> dict:
    if quantity < 1:
        raise ValueError('quantity must be >= 1')
    item = CartItem.objects.filter(user_id=user_id, variant_id=variant_id).first()
    if not item:
        raise LookupError('Cart item not found')
    item.quantity = quantity
    item.save(update_fields=['quantity', 'updated_at'])
    return list_cart(user_id)


def remove_cart_item(user_id: str, variant_id: str) -> dict:
    CartItem.objects.filter(user_id=user_id, variant_id=variant_id).delete()
    return list_cart(user_id)


def clear_cart(user_id: str) -> dict:
    CartItem.objects.filter(user_id=user_id).delete()
    return list_cart(user_id)


def list_reviews(page: int, limit: int, source: str | None = None) -> dict:
    qs = Review.objects.filter(is_published=True)
    if source and source not in ('all', ''):
        qs = qs.filter(source=source)
    total = qs.count()
    rows = qs[(page - 1) * limit : page * limit]
    data = [
        {
            'id': str(r.id),
            'authorName': r.author_name,
            'text': r.text,
            'rating': r.rating,
            'source': r.source,
            'createdAt': r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {'data': data, 'count': total, 'page': page, 'limit': limit}


def list_video_reviews(page: int, limit: int) -> dict:
    qs = Review.objects.filter(is_published=True).exclude(video_url='').order_by('-created_at')
    total = qs.count()
    rows = qs[(page - 1) * limit : page * limit]
    data = [
        {
            'id': str(r.id),
            'authorName': r.author_name,
            'videoUrl': r.video_url,
            'thumbnail': media_url(r.thumbnail),
            'rating': r.rating,
            'source': r.source,
            'createdAt': r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return {'data': data, 'count': total, 'page': page, 'limit': limit}


def create_review(data: dict, thumbnail_file=None) -> dict:
    r = Review.objects.create(
        author_name=data['authorName'],
        text=data.get('text') or '',
        rating=int(data.get('rating') or 5),
        source=data.get('source') or Review.SOURCE_SITE,
        video_url=data.get('videoUrl') or '',
        is_published=bool(data.get('isPublished', True)),
    )
    if thumbnail_file:
        r.thumbnail = thumbnail_file
        r.save(update_fields=['thumbnail'])
    return {'id': str(r.id)}


def update_review(pk: str, data: dict, thumbnail_file=None) -> dict:
    r = Review.objects.get(pk=pk)
    for key, attr in (
        ('authorName', 'author_name'),
        ('text', 'text'),
        ('rating', 'rating'),
        ('source', 'source'),
        ('videoUrl', 'video_url'),
        ('isPublished', 'is_published'),
    ):
        if key in data:
            setattr(r, attr, data[key])
    if thumbnail_file:
        r.thumbnail = thumbnail_file
    r.save()
    return {'id': str(r.id)}


def delete_review(pk: str) -> None:
    Review.objects.filter(pk=pk).delete()


def get_site_settings() -> dict[str, Any]:
    row, _ = SiteSettings.objects.get_or_create(pk=1)
    categories = []
    for cat in Category.objects.order_by('name').values('id', 'name', 'slug', 'icon'):
        categories.append(
            {
                'id': cat['id'],
                'name': cat['name'],
                'slug': cat['slug'],
                'icon': media_url(cat['icon']),
            }
        )
    brands = list(
        Product.objects.values_list('brand__name', flat=True)
        .distinct()
        .order_by('brand__name')[:20]
    )
    popular = list(
        Product.objects.filter(is_hit=True)
        .order_by('-created_at')
        .values_list('title', flat=True)[:8]
    )
    if not popular:
        popular = list(
            Product.objects.order_by('-created_at').values_list('title', flat=True)[:8]
        )
    advantages = row.advantages if row.advantages else DEFAULT_ADVANTAGES
    return {
        'phone': row.phone,
        'email': row.email,
        'address': row.address,
        'social': {
            'telegram': row.telegram_url,
            'vk': row.vk_url,
            'whatsapp': row.whatsapp_url,
        },
        'map': {'lat': row.map_lat, 'lng': row.map_lng},
        'advantages': advantages,
        'categories': categories,
        'brands': [b for b in brands if b],
        'popularSearches': [t for t in popular if t],
        'updatedAt': row.updated_at.isoformat() if row.updated_at else None,
    }


def search_suggest(query: str, limit: int = 8) -> dict[str, Any]:
    q = (query or '').strip()
    if not q:
        return {'products': [], 'tags': []}
    products_qs = (
        Product.objects.select_related('brand', 'category')
        .filter(Q(title__icontains=q) | Q(description__icontains=q))
        .order_by('-is_hit', '-created_at')[:limit]
    )
    products = []
    for p in products_qs:
        v = (
            ProductVariant.objects.filter(product_id=p.id, is_available=True)
            .select_related('memory', 'color')
            .order_by('price')
            .first()
        )
        if v:
            products.append(variant_card(v))
        else:
            products.append(
                {
                    'variantId': None,
                    'productId': p.id,
                    'title': p.title,
                    'slug': p.slug,
                    'price': None,
                    'image': None,
                    'brand': {'id': p.brand_id, 'name': p.brand.name},
                }
            )
    tags = list(
        ProductModel.objects.filter(name__icontains=q)
        .values_list('name', flat=True)
        .distinct()[:6]
    )
    if not tags:
        tags = [p['title'] for p in products[:3]]
    return {'products': products, 'tags': tags}


def related_products(slug: str, limit: int = 4) -> list[dict]:
    product = Product.objects.filter(slug=slug).first()
    if not product:
        return []
    qs = (
        Product.objects.select_related('brand', 'category', 'condition', 'product_model')
        .prefetch_related(*product_list_prefetch())
        .filter(category_id=product.category_id)
        .exclude(pk=product.pk)
        .order_by('-is_hit', '-created_at')[:limit]
    )
    return [product_to_dict(p, variants=list(p.variants.all())) for p in qs]


def related_blogs(slug: str, limit: int = 3) -> list[dict]:
    from apps.store_core.models import Blog

    current = Blog.objects.filter(slug=slug).first()
    qs = Blog.objects.order_by('-created_at')
    if current:
        qs = qs.exclude(pk=current.pk)
    rows = qs[:limit]
    return [
        {
            'id': str(b.id),
            'title': b.title,
            'slug': b.slug,
            'image': media_url(b.image),
            'createdAt': b.created_at.isoformat() if b.created_at else None,
        }
        for b in rows
    ]

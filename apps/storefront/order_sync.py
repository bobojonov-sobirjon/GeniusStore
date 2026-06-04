from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.catalog.serialization import product_gallery_images
from apps.common.media_urls import media_url
from apps.common.uuid_utils import normalize_uuid
from apps.store_core.models import OrderItem, ProductVariant, StoreOrder


def _first_image(images) -> str | None:
    if not images or not isinstance(images, list):
        return None
    first = images[0]
    if isinstance(first, str):
        return first
    if isinstance(first, dict):
        return first.get('url') or first.get('path') or first.get('src')
    return None


def _resolve_variant(product_id: Any) -> ProductVariant | None:
    if product_id is None:
        return None
    uid = normalize_uuid(str(product_id))
    if uid:
        return (
            ProductVariant.objects.select_related('product', 'memory', 'color')
            .filter(pk=uid, is_available=True)
            .first()
        )
    try:
        pid = int(product_id)
    except (TypeError, ValueError):
        return None
    return (
        ProductVariant.objects.select_related('product', 'memory', 'color')
        .filter(product_id=pid, is_available=True)
        .order_by('price')
        .first()
    )


def _line_payload(item: OrderItem) -> dict[str, Any]:
    v = item.product_variant
    p = v.product
    return {
        'product_id': str(v.id),
        'productId': p.id,
        'title': p.title,
        'slug': p.slug,
        'quantity': item.quantity,
        'unitPrice': item.unit_price,
        'lineTotal': item.line_total,
        'image': media_url(_first_image(product_gallery_images(p) or v.images)),
        'memory': {'id': v.memory_id, 'name': v.memory.name} if v.memory_id else None,
        'color': {'id': v.color_id, 'name': v.color.name, 'hex': v.color.hex} if v.color_id else None,
    }


def order_to_dict(order: StoreOrder) -> dict[str, Any]:
    items = list(order.items.select_related('product_variant__product', 'product_variant__memory', 'product_variant__color'))
    return {
        'id': str(order.id),
        'fullName': order.full_name,
        'email': order.email,
        'phone': order.phone,
        'totalPrice': order.total_sum,
        'isDelivery': order.is_delivery,
        'isPickup': order.is_pickup,
        'deliveryType': order.delivery_type,
        'apartment': order.apartment,
        'entrance': order.entrance,
        'floor': order.floor,
        'products_list': [_line_payload(item) for item in items],
        'createdAt': order.created_at.isoformat() if order.created_at else None,
        'updatedAt': order.updated_at.isoformat() if order.updated_at else None,
    }


def _parse_delivery_type(data: dict) -> str:
    is_delivery = data.get('isDelivery', data.get('is_delivery'))
    is_pickup = data.get('isPickup', data.get('is_pickup'))
    if is_delivery is not None or is_pickup is not None:
        delivery = bool(is_delivery)
        pickup = bool(is_pickup)
        if delivery and pickup:
            raise ValueError('Укажите только один способ получения: доставка или самовывоз')
        if pickup:
            return StoreOrder.DeliveryType.PICKUP
        if delivery:
            return StoreOrder.DeliveryType.DELIVERY
        raise ValueError('Укажите isDelivery или isPickup')
    raw = (data.get('deliveryType') or data.get('delivery_type') or '').strip().lower()
    if raw in ('pickup', 'samovivoz', 'самовывоз'):
        return StoreOrder.DeliveryType.PICKUP
    if raw in ('delivery', 'dostavka', 'доставка', ''):
        return StoreOrder.DeliveryType.DELIVERY
    raise ValueError('Неверный deliveryType')


def _parse_contact(data: dict) -> tuple[str, str, str]:
    full_name = str(data.get('fullName') or data.get('full_name') or data.get('fio') or '').strip()
    email = str(data.get('email') or '').strip()
    phone = str(data.get('phone') or '').strip()
    if not full_name:
        raise ValueError('fullName обязателен')
    if not email:
        raise ValueError('email обязателен')
    if not phone:
        raise ValueError('phone обязателен')
    return full_name, email, phone


def _parse_products_list(data: dict) -> list[dict]:
    rows = data.get('products_list') or data.get('productsList') or data.get('products') or []
    if not isinstance(rows, list) or not rows:
        raise ValueError('products_list обязателен и не может быть пустым')
    out = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Каждый элемент products_list должен быть объектом')
        product_id = row.get('product_id') or row.get('productId') or row.get('variantId') or row.get('variant_id')
        quantity = int(row.get('quantity') or 0)
        if not product_id:
            raise ValueError('product_id обязателен в каждой позиции')
        if quantity < 1:
            raise ValueError('quantity должен быть >= 1')
        out.append({'product_id': product_id, 'quantity': quantity})
    return out


def create_order(data: dict) -> dict:
    products_list = _parse_products_list(data)
    delivery_type = _parse_delivery_type(data)
    full_name, email, phone = _parse_contact(data)
    apartment = str(data.get('apartment') or data.get('kvartira') or '').strip()
    entrance = str(data.get('entrance') or data.get('podezd') or '').strip()
    floor = str(data.get('floor') or data.get('etazh') or '').strip()

    with transaction.atomic():
        order = StoreOrder.objects.create(
            user_id=None,
            total_sum=0,
            delivery_type=delivery_type,
            apartment=apartment,
            entrance=entrance,
            floor=floor,
            full_name=full_name,
            email=email,
            phone=phone,
            products=[],
        )
        total = 0
        for row in products_list:
            variant = _resolve_variant(row['product_id'])
            if not variant:
                raise LookupError(f"Товар не найден: {row['product_id']}")
            line_total = int(variant.price * row['quantity'])
            OrderItem.objects.create(
                order=order,
                product_variant=variant,
                quantity=row['quantity'],
                unit_price=int(variant.price),
                line_total=line_total,
            )
            total += line_total
        order.total_sum = total
        order.save(update_fields=['total_sum', 'updated_at'])

    order = StoreOrder.objects.prefetch_related(
        'items__product_variant__product',
        'items__product_variant__memory',
        'items__product_variant__color',
    ).get(pk=order.id)
    return order_to_dict(order)


def list_orders_by_email(email: str) -> list[dict]:
    qs = (
        StoreOrder.objects.filter(email__iexact=email.strip())
        .prefetch_related('items__product_variant__product', 'items__product_variant__memory', 'items__product_variant__color')
        .order_by('-created_at')
    )
    return [order_to_dict(order) for order in qs]


def get_order(order_id: str) -> dict | None:
    uid = normalize_uuid(order_id)
    if not uid:
        return None
    order = (
        StoreOrder.objects.filter(pk=uid)
        .prefetch_related('items__product_variant__product', 'items__product_variant__memory', 'items__product_variant__color')
        .first()
    )
    if not order:
        return None
    return order_to_dict(order)

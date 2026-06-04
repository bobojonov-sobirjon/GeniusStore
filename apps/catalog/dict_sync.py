from __future__ import annotations

import uuid
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.common.media_urls import media_url
from apps.common.slugify_store import generate_slug
from apps.store_core.models import Brand, Category, Color, Condition, Memory, ProductModel, SimType


def color_list():
    return list(Color.objects.order_by('id').values())


def color_one(pk: int):
    return Color.objects.filter(pk=pk).values().first()


def color_create(data: dict) -> dict:
    c = Color.objects.create(name=data['name'], hex=data.get('hex'))
    return {'id': c.id, 'name': c.name, 'hex': c.hex, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def color_update(pk: int, data: dict) -> dict:
    c = Color.objects.get(pk=pk)
    if 'name' in data:
        c.name = data['name']
    if 'hex' in data:
        c.hex = data.get('hex')
    c.updated_at = timezone.now()
    c.save()
    return {'id': c.id, 'name': c.name, 'hex': c.hex, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def color_delete(pk: int) -> None:
    Color.objects.filter(pk=pk).delete()


def memory_list():
    return list(Memory.objects.order_by('id').values())


def memory_one(pk: int):
    return Memory.objects.filter(pk=pk).values().first()


def memory_create(data: dict) -> dict:
    m = Memory.objects.create(name=data['name'])
    return {'id': m.id, 'name': m.name, 'createdAt': m.created_at}


def memory_update(pk: int, data: dict) -> dict:
    m = Memory.objects.get(pk=pk)
    m.name = data.get('name', m.name)
    m.save()
    return {'id': m.id, 'name': m.name, 'createdAt': m.created_at}


def memory_delete(pk: int) -> None:
    Memory.objects.filter(pk=pk).delete()


def brand_list():
    return list(Brand.objects.order_by('id').values())


def brand_one(pk: int):
    return Brand.objects.filter(pk=pk).values().first()


def brand_create(data: dict) -> dict:
    b = Brand.objects.create(name=data['name'])
    return {'id': b.id, 'name': b.name, 'createdAt': b.created_at}


def brand_update(pk: int, data: dict) -> dict:
    b = Brand.objects.get(pk=pk)
    b.name = data.get('name', b.name)
    b.save()
    return {'id': b.id, 'name': b.name, 'createdAt': b.created_at}


def brand_delete(pk: int) -> None:
    Brand.objects.filter(pk=pk).delete()


def category_list():
    return list(Category.objects.order_by('created_at').values())


def category_one(pk: int):
    return Category.objects.filter(pk=pk).values().first()


def category_create(data: dict, icon_file) -> dict:
    c = Category.objects.create(name=data['name'], icon=icon_file)
    return {
        'id': c.id,
        'name': c.name,
        'icon': media_url(c.icon),
        'slug': c.slug,
        'createdAt': c.created_at,
    }


def category_set_slugs() -> str:
    for c in Category.objects.all():
        if not c.slug:
            c.slug = generate_slug(c.name)
            c.save(update_fields=['slug'])
    return "Kategoriyalar slugga o'zgartirildi"


def category_update(pk: int, data: dict, icon_file) -> dict:
    c = Category.objects.get(pk=pk)
    if icon_file:
        c.icon = icon_file
    if data.get('name'):
        c.name = data['name']
    c.save()
    return {
        'id': c.id,
        'name': c.name,
        'icon': media_url(c.icon),
        'slug': c.slug,
        'createdAt': c.created_at,
    }


def category_delete(pk: int) -> None:
    Category.objects.filter(pk=pk).delete()


def condition_list():
    return list(Condition.objects.order_by('created_at').values())


def condition_one(pk: str):
    return Condition.objects.filter(pk=pk).values().first()


def condition_create(data: dict) -> dict:
    c = Condition.objects.create(id=str(uuid.uuid4()), name=data['name'])
    return {'id': str(c.id), 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def condition_update(pk: str, data: dict) -> dict:
    c = Condition.objects.get(pk=pk)
    c.name = data.get('name', c.name)
    c.updated_at = timezone.now()
    c.save()
    return {'id': str(c.id), 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def condition_delete(pk: str) -> None:
    Condition.objects.filter(pk=pk).delete()


def simtype_list():
    return list(SimType.objects.order_by('id').values())


def simtype_one(pk: str):
    return SimType.objects.filter(pk=pk).values().first()


def simtype_create(data: dict) -> dict:
    s = SimType.objects.create(id=str(uuid.uuid4()), name=data['name'])
    return {'id': str(s.id), 'name': s.name}


def simtype_update(pk: str, data: dict) -> dict:
    s = SimType.objects.get(pk=pk)
    s.name = data.get('name', s.name)
    s.save()
    return {'id': str(s.id), 'name': s.name}


def simtype_delete(pk: str) -> None:
    SimType.objects.filter(pk=pk).delete()


def product_model_list():
    return list(ProductModel.objects.order_by('id').values())


def product_model_one(pk: int):
    return ProductModel.objects.filter(pk=pk).values().first()


def product_model_create(data: dict) -> dict:
    m = ProductModel.objects.create(name=data['name'])
    return {'id': m.id, 'name': m.name, 'createdAt': m.created_at}


def product_model_update(pk: int, data: dict) -> dict:
    m = ProductModel.objects.get(pk=pk)
    m.name = data.get('name', m.name)
    m.save()
    return {'id': m.id, 'name': m.name, 'createdAt': m.created_at}


def product_model_delete(pk: int) -> None:
    ProductModel.objects.filter(pk=pk).delete()

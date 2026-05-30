from __future__ import annotations

import uuid

from django.utils import timezone

from apps.common.file_storage import save_upload_file
from apps.store_core.models import Banner, Info


def banner_create(data: dict, img_pc, img_mobile) -> Banner:
    if img_pc or img_mobile:
        pc = save_upload_file('image', img_pc) if img_pc else save_upload_file('image', img_mobile)
        mob = save_upload_file('image', img_mobile) if img_mobile else pc
    else:
        pc = mob = ''
    return Banner.objects.create(
        id=str(uuid.uuid4()),
        title=data['title'],
        description=data['description'],
        img_pc=pc,
        img_mobile=mob,
    )


def banner_list():
    return list(Banner.objects.order_by('-created_at').values())


def banner_one(pk: str):
    return Banner.objects.filter(pk=pk).values().first()


def banner_update(pk: str, data: dict, img_pc, img_mobile) -> dict:
    b = Banner.objects.get(pk=pk)
    if data.get('title'):
        b.title = data['title']
    if data.get('description') is not None:
        b.description = data['description']
    if img_pc:
        b.img_pc = save_upload_file('image', img_pc)
    if img_mobile:
        b.img_mobile = save_upload_file('image', img_mobile)
    b.updated_at = timezone.now()
    b.save()
    return banner_one(str(b.id))


def banner_delete(pk: str) -> None:
    Banner.objects.filter(pk=pk).delete()


def info_create(data: dict) -> Info:
    return Info.objects.create(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description') or '',
    )


def info_list():
    return list(Info.objects.order_by('-created_at').values())


def info_one(pk: str):
    return Info.objects.filter(pk=pk).values().first()


def info_update(pk: str, data: dict) -> dict:
    i = Info.objects.get(pk=pk)
    if data.get('name'):
        i.name = data['name']
    if 'description' in data:
        i.description = data.get('description') or ''
    i.updated_at = timezone.now()
    i.save()
    return info_one(str(i.id))


def info_delete(pk: str) -> None:
    Info.objects.filter(pk=pk).delete()

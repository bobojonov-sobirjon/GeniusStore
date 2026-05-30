from __future__ import annotations

import uuid

from django.utils import timezone

from apps.common.file_storage import save_upload_file
from apps.common.slugify_store import generate_slug
from apps.store_core.models import Service, ServiceBrand, ServiceModel


def brand_create(data: dict, image) -> ServiceBrand:
    if not image:
        raise ValueError('image required')
    path = save_upload_file('image', image)
    return ServiceBrand.objects.create(
        id=str(uuid.uuid4()),
        name=data['name'],
        slug=generate_slug(data['name']),
        image=path,
    )


def brand_page(page: int, limit: int):
    qs = ServiceBrand.objects.order_by('created_at')[(page - 1) * limit : page * limit]
    return {'data': list(qs.values()), 'count': ServiceBrand.objects.count()}


def brand_by_model():
    data = []
    for b in ServiceBrand.objects.prefetch_related('models').order_by('created_at'):
        data.append(
            {
                'id': str(b.id),
                'name': b.name,
                'slug': b.slug,
                'image': b.image,
                'models': list(b.models.values()),
            }
        )
    return data


def brand_models(id_: str):
    b = ServiceBrand.objects.prefetch_related('models').filter(pk=id_).first()
    if not b:
        return None
    return {
        'id': str(b.id),
        'name': b.name,
        'slug': b.slug,
        'image': b.image,
        'models': list(b.models.values()),
    }


def brand_by_slug_models(slug: str):
    b = ServiceBrand.objects.prefetch_related('models').filter(slug=slug).first()
    if not b:
        return None
    return brand_models(str(b.id))


def brand_one(id_: str):
    return ServiceBrand.objects.filter(pk=id_).values().first()


def brand_update(id_: str, data: dict, image) -> dict:
    b = ServiceBrand.objects.get(pk=id_)
    if image:
        b.image = save_upload_file('image', image)
    if data.get('name'):
        b.name = data['name']
        b.slug = generate_slug(data['name'])
    b.updated_at = timezone.now()
    b.save()
    return brand_one(str(b.id))


def brand_delete(id_: str) -> None:
    ServiceBrand.objects.filter(pk=id_).delete()


def sm_create(data: dict) -> ServiceModel:
    return ServiceModel.objects.create(
        id=str(uuid.uuid4()),
        name=data['name'],
        slug=generate_slug(data['name']),
        service_brand_id=data.get('serviceBrandId'),
    )


def sm_page(page: int, limit: int):
    qs = ServiceModel.objects.order_by('created_at')[(page - 1) * limit : page * limit]
    return {'data': list(qs.values()), 'count': ServiceModel.objects.count()}


def sm_one(id_: str):
    return ServiceModel.objects.filter(pk=id_).values().first()


def sm_by_slug(slug: str):
    m = ServiceModel.objects.prefetch_related('services').filter(slug=slug).first()
    if not m:
        return None
    return {
        'id': str(m.id),
        'name': m.name,
        'slug': m.slug,
        'serviceBrandId': str(m.service_brand_id) if m.service_brand_id else None,
        'createdAt': m.created_at,
        'updatedAt': m.updated_at,
        'services': list(m.services.values()),
    }


def sm_update(id_: str, data: dict) -> dict:
    m = ServiceModel.objects.get(pk=id_)
    if data.get('name'):
        m.name = data['name']
        m.slug = generate_slug(data['name'])
    m.updated_at = timezone.now()
    m.save()
    return sm_one(str(m.id))


def sm_delete(id_: str) -> None:
    ServiceModel.objects.filter(pk=id_).delete()


def svc_create(data: dict) -> Service:
    return Service.objects.create(
        id=str(uuid.uuid4()),
        name=data['name'],
        slug=generate_slug(data['name']),
        labor_only=int(data['laborOnly']),
        labor_with_part=int(data['laborWithPart']),
        service_model_id=data.get('serviceModelId'),
    )


def svc_page(page: int, limit: int):
    qs = Service.objects.order_by('created_at')[(page - 1) * limit : page * limit]
    return {'data': list(qs.values()), 'count': Service.objects.count()}


def svc_one(id_: str):
    return Service.objects.filter(pk=id_).select_related('service_model').values().first()


def svc_by_slug(slug: str):
    s = Service.objects.select_related('service_model').filter(slug=slug).first()
    if not s:
        return None
    out = {
        'id': str(s.id),
        'name': s.name,
        'slug': s.slug,
        'laborOnly': s.labor_only,
        'laborWithPart': s.labor_with_part,
        'serviceModelId': str(s.service_model_id) if s.service_model_id else None,
        'createdAt': s.created_at,
        'updatedAt': s.updated_at,
    }
    if s.service_model:
        out['serviceModel'] = {'id': str(s.service_model.id), 'name': s.service_model.name, 'slug': s.service_model.slug}
    return out


def svc_update(id_: str, data: dict) -> dict:
    s = Service.objects.get(pk=id_)
    if data.get('name'):
        s.name = data['name']
        s.slug = generate_slug(data['name'])
    if 'laborOnly' in data:
        s.labor_only = int(data['laborOnly'])
    if 'laborWithPart' in data:
        s.labor_with_part = int(data['laborWithPart'])
    if 'serviceModelId' in data:
        s.service_model_id = data.get('serviceModelId')
    s.updated_at = timezone.now()
    s.save()
    return svc_one(str(s.id))


def svc_delete(id_: str) -> None:
    Service.objects.filter(pk=id_).delete()

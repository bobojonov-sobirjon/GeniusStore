from __future__ import annotations

import uuid

from django.utils import timezone

from apps.common.file_storage import save_upload_file
from apps.common.media_urls import media_url, serialize_values_list, serialize_values_row
from apps.common.slugify_store import generate_slug
from apps.common.uuid_utils import normalize_uuid
from apps.store_core.models import Blog, BlogCategory, BlogSteps

BLOG_MEDIA_FIELDS = ('image',)


def _blog_payload(b: Blog) -> dict:
    return {
        'id': str(b.id),
        'title': b.title,
        'slug': b.slug,
        'content': b.content,
        'blogCategoryId': str(b.blog_category_id),
        'image': media_url(b.image),
        'createdAt': b.created_at.isoformat() if b.created_at else None,
        'updatedAt': b.updated_at.isoformat() if b.updated_at else None,
        'blogSteps': serialize_values_list(list(b.blogSteps.order_by('created_at').values())),
    }


def blog_category_create(data: dict) -> dict:
    c = BlogCategory.objects.create(id=str(uuid.uuid4()), name=data['name'])
    return serialize_values_row(
        {'id': c.id, 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}
    )


def blog_category_list():
    return serialize_values_list(list(BlogCategory.objects.order_by('created_at').values()))


def blog_category_one(pk: str):
    uid = normalize_uuid(pk)
    if not uid:
        return None
    return serialize_values_row(BlogCategory.objects.filter(pk=uid).values().first())


def blog_category_update(pk: str, data: dict) -> dict:
    uid = normalize_uuid(pk)
    if not uid:
        raise LookupError('Category not found')
    c = BlogCategory.objects.get(pk=uid)
    c.name = data.get('name', c.name)
    c.updated_at = timezone.now()
    c.save()
    return serialize_values_row(
        {'id': c.id, 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}
    )


def blog_category_delete(pk: str) -> None:
    uid = normalize_uuid(pk)
    if not uid:
        return
    BlogCategory.objects.filter(pk=uid).delete()


def blog_create(data: dict, image) -> Blog:
    path = save_upload_file('image', image) if image else None
    return Blog.objects.create(
        id=str(uuid.uuid4()),
        title=data['title'],
        slug=generate_slug(data['title']),
        content=data['content'],
        blog_category_id=data.get('blogCategoryId') or data.get('blog_category_id'),
        image=path,
    )


def blog_by_cat(cat_id: str):
    uid = normalize_uuid(cat_id)
    if not uid:
        return []
    rows = []
    for b in Blog.objects.filter(blog_category_id=uid).order_by('-created_at'):
        rows.append(_blog_payload(b))
    return rows


def blog_all(page: int, limit: int):
    page = max(1, int(page))
    limit = max(1, min(int(limit), 100))
    qs = Blog.objects.order_by('-created_at').prefetch_related('blogSteps')[
        (page - 1) * limit : page * limit
    ]
    return {'data': [_blog_payload(b) for b in qs], 'count': Blog.objects.count()}


def blog_by_slug(slug: str) -> dict | None:
    b = Blog.objects.prefetch_related('blogSteps').filter(slug=slug).first()
    if not b:
        return None
    return _blog_payload(b)


def blog_one(pk: str) -> dict | None:
    uid = normalize_uuid(pk)
    if not uid:
        return None
    b = Blog.objects.prefetch_related('blogSteps').filter(pk=uid).first()
    if not b:
        return None
    return _blog_payload(b)


def blog_update(pk: str, data: dict, image) -> dict:
    uid = normalize_uuid(pk)
    if not uid:
        raise LookupError('Blog not found')
    b = Blog.objects.get(pk=uid)
    if image:
        b.image = save_upload_file('image', image)
    if data.get('title'):
        b.title = data['title']
        b.slug = generate_slug(data['title'])
    if data.get('content'):
        b.content = data['content']
    if data.get('blogCategoryId'):
        b.blog_category_id = data['blogCategoryId']
    b.updated_at = timezone.now()
    b.save()
    return blog_one(str(b.id)) or {}


def blog_delete(pk: str) -> None:
    uid = normalize_uuid(pk)
    if not uid:
        return
    Blog.objects.filter(pk=uid).delete()


def blog_steps_create(data: dict) -> dict:
    s = BlogSteps.objects.create(
        id=str(uuid.uuid4()),
        title=data['title'],
        content=data['content'],
        blog_id=data['blogId'],
    )
    return serialize_values_row(
        {'id': s.id, 'title': s.title, 'content': s.content, 'blogId': s.blog_id}
    )


def blog_steps_list():
    return serialize_values_list(list(BlogSteps.objects.order_by('created_at').values()))


def blog_steps_one(pk: str):
    uid = normalize_uuid(pk)
    if not uid:
        return None
    return serialize_values_row(BlogSteps.objects.filter(pk=uid).values().first())


def blog_steps_update(pk: str, data: dict) -> dict:
    uid = normalize_uuid(pk)
    if not uid:
        raise LookupError('Blog step not found')
    s = BlogSteps.objects.get(pk=uid)
    s.title = data.get('title', s.title)
    s.content = data.get('content', s.content)
    s.updated_at = timezone.now()
    s.save()
    return serialize_values_row(
        {'id': s.id, 'title': s.title, 'content': s.content, 'blogId': s.blog_id}
    )


def blog_steps_delete(pk: str) -> None:
    uid = normalize_uuid(pk)
    if not uid:
        return
    BlogSteps.objects.filter(pk=uid).delete()

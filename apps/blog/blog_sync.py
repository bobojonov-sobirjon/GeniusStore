from __future__ import annotations

import uuid

from django.utils import timezone

from apps.common.file_storage import save_upload_file
from apps.common.slugify_store import generate_slug
from apps.store_core.models import Blog, BlogCategory, BlogSteps


def blog_category_create(data: dict) -> dict:
    c = BlogCategory.objects.create(id=str(uuid.uuid4()), name=data['name'])
    return {'id': str(c.id), 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def blog_category_list():
    return list(BlogCategory.objects.order_by('created_at').values())


def blog_category_one(pk: str):
    return BlogCategory.objects.filter(pk=pk).values().first()


def blog_category_update(pk: str, data: dict) -> dict:
    c = BlogCategory.objects.get(pk=pk)
    c.name = data.get('name', c.name)
    c.updated_at = timezone.now()
    c.save()
    return {'id': str(c.id), 'name': c.name, 'createdAt': c.created_at, 'updatedAt': c.updated_at}


def blog_category_delete(pk: str) -> None:
    BlogCategory.objects.filter(pk=pk).delete()


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
    return list(Blog.objects.filter(blog_category_id=cat_id).values())


def blog_all(page: int, limit: int):
    qs = Blog.objects.order_by('created_at').prefetch_related('blogSteps')[(page - 1) * limit : page * limit]
    out = []
    for b in qs:
        out.append(
            {
                'id': str(b.id),
                'title': b.title,
                'slug': b.slug,
                'content': b.content,
                'blogCategoryId': str(b.blog_category_id),
                'image': b.image,
                'createdAt': b.created_at,
                'updatedAt': b.updated_at,
                'blogSteps': list(b.blogSteps.order_by('id').values()),
            }
        )
    return {'data': out, 'count': Blog.objects.count()}


def blog_by_slug(slug: str) -> dict | None:
    b = Blog.objects.prefetch_related('blogSteps').filter(slug=slug).first()
    if not b:
        return None
    return {
        'id': str(b.id),
        'title': b.title,
        'slug': b.slug,
        'content': b.content,
        'blogCategoryId': str(b.blog_category_id),
        'image': b.image,
        'createdAt': b.created_at,
        'updatedAt': b.updated_at,
        'blogSteps': list(b.blogSteps.order_by('id').values()),
    }


def blog_one(pk: str) -> dict | None:
    b = Blog.objects.prefetch_related('blogSteps').filter(pk=pk).first()
    if not b:
        return None
    return blog_by_slug(b.slug) if b else None


def blog_update(pk: str, data: dict, image) -> dict:
    b = Blog.objects.get(pk=pk)
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
    Blog.objects.filter(pk=pk).delete()


def blog_steps_create(data: dict) -> dict:
    s = BlogSteps.objects.create(
        id=str(uuid.uuid4()),
        title=data['title'],
        content=data['content'],
        blog_id=data['blogId'],
    )
    return {'id': str(s.id), 'title': s.title, 'content': s.content, 'blogId': str(s.blog_id)}


def blog_steps_list():
    return list(BlogSteps.objects.order_by('created_at').values())


def blog_steps_one(pk: str):
    return BlogSteps.objects.filter(pk=pk).values().first()


def blog_steps_update(pk: str, data: dict) -> dict:
    s = BlogSteps.objects.get(pk=pk)
    s.title = data.get('title', s.title)
    s.content = data.get('content', s.content)
    s.updated_at = timezone.now()
    s.save()
    return {'id': str(s.id), 'title': s.title, 'content': s.content, 'blogId': str(s.blog_id)}


def blog_steps_delete(pk: str) -> None:
    BlogSteps.objects.filter(pk=pk).delete()

from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.common.views import APIView

from apps.blog import blog_sync as b
from apps.common.openapi_requests import (
    REQ_BLOG_CATEGORY_WRITE,
    REQ_BLOG_CREATE_JSON,
    REQ_BLOG_CREATE_MULTIPART,
    REQ_BLOG_PATCH_JSON,
    REQ_BLOG_PATCH_MULTIPART,
    REQ_BLOG_STEPS_PATCH,
    REQ_BLOG_STEPS_WRITE,
)


@extend_schema(tags=['Блог — Категории'])
class BlogCategoryRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список категорий блога',
        description='Все категории статей (id, название, slug и связанные поля по схеме БД).',
    )
    async def get(self, request):
        return Response(await sync_to_async(b.blog_category_list)())

    @extend_schema(
        summary='Создать категорию блога',
        description='Тело JSON: поле `name` (обязательно).',
        request=REQ_BLOG_CATEGORY_WRITE,
    )
    async def post(self, request):
        return Response(await sync_to_async(b.blog_category_create)(dict(request.data)))


@extend_schema(tags=['Блог — Категории'])
class BlogCategoryDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Категория по id',
        description='UUID категории в пути.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(b.blog_category_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить категорию',
        description='Частичное обновление полей категории.',
        request=REQ_BLOG_CATEGORY_WRITE,
    )
    async def patch(self, request, pk: str):
        return Response(await sync_to_async(b.blog_category_update)(str(pk), dict(request.data)))

    @extend_schema(
        summary='Удалить категорию',
        description='Удаление записи категории.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(b.blog_category_delete)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Блог — Статьи'])
class BlogRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Создать статью блога',
        description='`application/json` — без картинки; `multipart/form-data` — с опциональным файлом `image`.',
        request={
            'application/json': REQ_BLOG_CREATE_JSON,
            'multipart/form-data': REQ_BLOG_CREATE_MULTIPART,
        },
    )
    async def post(self, request):
        blog = await sync_to_async(b.blog_create)(dict(request.data), request.FILES.get('image'))
        return Response({'id': str(blog.id), 'slug': blog.slug})


@extend_schema(tags=['Блог — Статьи'])
class BlogByCatView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Статьи по категории',
        description='UUID категории в пути. Список постов, относящихся к этой категории.',
    )
    async def get(self, request, cat_id: str):
        return Response(await sync_to_async(b.blog_by_cat)(str(cat_id)))


@extend_schema(tags=['Блог — Статьи'])
class BlogPagedView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Все статьи с пагинацией',
        description='Параметры пути: `page`, `limit` — нумерация страниц и размер страницы.',
    )
    async def get(self, request, page: int, limit: int):
        return Response(await sync_to_async(b.blog_all)(int(page), int(limit)))


@extend_schema(tags=['Блог — Статьи'])
class BlogSlugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Статья по slug',
        description='Публичная карточка статьи для ЧПУ-URL.',
    )
    async def get(self, request, slug: str):
        row = await sync_to_async(b.blog_by_slug)(slug)
        if not row:
            raise NotFound()
        return Response(row)


@extend_schema(tags=['Блог — Статьи'])
class BlogDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Статья по id',
        description='UUID статьи.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(b.blog_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить статью',
        description='JSON или multipart с опциональным `image`.',
        request={
            'application/json': REQ_BLOG_PATCH_JSON,
            'multipart/form-data': REQ_BLOG_PATCH_MULTIPART,
        },
    )
    async def patch(self, request, pk: str):
        return Response(await sync_to_async(b.blog_update)(str(pk), dict(request.data), request.FILES.get('image')))

    @extend_schema(
        summary='Удалить статью',
        description='Полное удаление записи блога.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(b.blog_delete)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Блог — Шаги'])
class BlogStepsRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список шагов (инструкции)',
        description='Все записи блока «шаги» для лендингов или гайдов.',
    )
    async def get(self, request):
        return Response(await sync_to_async(b.blog_steps_list)())

    @extend_schema(
        summary='Создать шаг',
        description='Поля шага: title, content, blogId (UUID статьи).',
        request=REQ_BLOG_STEPS_WRITE,
    )
    async def post(self, request):
        return Response(await sync_to_async(b.blog_steps_create)(dict(request.data)))


@extend_schema(tags=['Блог — Шаги'])
class BlogStepsDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Шаг по id',
        description='UUID записи шага.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(b.blog_steps_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить шаг',
        description='Частичное обновление полей шага.',
        request=REQ_BLOG_STEPS_PATCH,
    )
    async def patch(self, request, pk: str):
        return Response(await sync_to_async(b.blog_steps_update)(str(pk), dict(request.data)))

    @extend_schema(
        summary='Удалить шаг',
        description='Удаление записи шага.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(b.blog_steps_delete)(str(pk))
        return Response(status=204)

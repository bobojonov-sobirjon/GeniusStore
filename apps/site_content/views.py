from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.common.views import APIView

from apps.common.openapi_requests import (
    REQ_BANNER_CREATE,
    REQ_BANNER_PATCH,
    REQ_INFO_PATCH,
    REQ_INFO_WRITE,
)
from apps.site_content import site_sync as s


@extend_schema(tags=['Сайт — Баннеры'])
class BannerRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список баннеров',
        description='Все баннеры главной и промо-блоков с путями к изображениям для ПК и мобильных.',
    )
    async def get(self, request):
        return Response(await sync_to_async(s.banner_list)())

    @extend_schema(
        summary='Создать баннер',
        description='Multipart: поля баннера + файлы `imgPc`, `imgMobile` (при отсутствии может вернуться ошибка валидации).',
        request={'multipart/form-data': REQ_BANNER_CREATE},
    )
    async def post(self, request):
        try:
            b = await sync_to_async(s.banner_create)(
                dict(request.data), request.FILES.get('imgPc'), request.FILES.get('imgMobile')
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response({'id': str(b.id)})


@extend_schema(tags=['Сайт — Баннеры'])
class BannerDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Баннер по id',
        description='UUID баннера.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(s.banner_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить баннер',
        description='JSON-поля и при необходимости новые файлы `imgPc` / `imgMobile`.',
        request={'multipart/form-data': REQ_BANNER_PATCH},
    )
    async def patch(self, request, pk: str):
        return Response(
            await sync_to_async(s.banner_update)(
                str(pk), dict(request.data), request.FILES.get('imgPc'), request.FILES.get('imgMobile')
            )
        )

    @extend_schema(
        summary='Удалить баннер',
        description='Удаление записи и связанных медиа по логике sync-слоя.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(s.banner_delete)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Сайт — Страницы'])
class InfoRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список информационных страниц',
        description='Страницы типа «О доставке», «Оплата», юридический текст и т.п.',
    )
    async def get(self, request):
        return Response(await sync_to_async(s.info_list)())

    @extend_schema(
        summary='Создать информационную страницу',
        description='Тело: заголовок, slug, HTML/текст и другие поля по модели.',
        request=REQ_INFO_WRITE,
    )
    async def post(self, request):
        i = await sync_to_async(s.info_create)(dict(request.data))
        return Response({'id': str(i.id)})


@extend_schema(tags=['Сайт — Страницы'])
class InfoDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Инфо-страница по id',
        description='UUID записи.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(s.info_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить инфо-страницу',
        description='Частичное обновление контента и метаданных.',
        request=REQ_INFO_PATCH,
    )
    async def patch(self, request, pk: str):
        return Response(await sync_to_async(s.info_update)(str(pk), dict(request.data)))

    @extend_schema(
        summary='Удалить инфо-страницу',
        description='Удаление страницы из CMS.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(s.info_delete)(str(pk))
        return Response(status=204)

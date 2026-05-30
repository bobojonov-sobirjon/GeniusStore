from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.authentication import AdminBearerAuthentication, StoreAdminPrincipal
from apps.common.openapi_requests import (
    REQ_SERVICE_BRAND_CREATE,
    REQ_SERVICE_BRAND_PATCH,
    REQ_SERVICE_CREATE,
    REQ_SERVICE_MODEL_CREATE,
    REQ_SERVICE_MODEL_PATCH,
    REQ_SERVICE_PATCH,
)
from apps.repair import repair_sync as r


def _require_admin(request):
    if not isinstance(request.user, StoreAdminPrincipal):
        raise PermissionDenied()


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandCreateView(APIView):
    authentication_classes = [AdminBearerAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Создать бренд сервиса',
        description='Только админ (Bearer). Multipart: имя, slug при необходимости, файл `image`. Ошибка 400 при дубликате slug.',
        request={'multipart/form-data': REQ_SERVICE_BRAND_CREATE},
    )
    async def post(self, request):
        _require_admin(request)
        try:
            b = await sync_to_async(r.brand_create)(dict(request.data), request.FILES.get('image'))
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response({'id': str(b.id), 'name': b.name, 'slug': b.slug, 'image': b.image})


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandPageView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список брендов сервиса (пагинация)',
        description='Параметры пути: `page`, `limit`. Публичный список брендов для раздела ремонта.',
    )
    async def get(self, request, page: int, limit: int):
        return Response(await sync_to_async(r.brand_page)(int(page), int(limit)))


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandByModelView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Все бренды с вложенными моделями',
        description='Дерево бренд → модели для навигации по ремонту без отдельных запросов на каждый бренд.',
    )
    async def get(self, request):
        return Response(await sync_to_async(r.brand_by_model)())


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandModelsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Модели выбранного бренда',
        description='UUID бренда в пути. 404, если бренд не найден.',
    )
    async def get(self, request, brand_id: str):
        data = await sync_to_async(r.brand_models)(str(brand_id))
        if not data:
            raise NotFound()
        return Response(data)


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandSlugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Бренд и модели по slug',
        description='ЧПУ бренда: карточка бренда со списком моделей для страницы раздела ремонта.',
    )
    async def get(self, request, slug: str):
        data = await sync_to_async(r.brand_by_slug_models)(slug)
        if not data:
            raise NotFound()
        return Response(data)


@extend_schema(tags=['Ремонт — Бренды'])
class ServiceBrandDetailView(APIView):
    permission_classes = [AllowAny]

    def get_authenticators(self):
        if getattr(self, 'request', None) and self.request.method in ('PATCH', 'DELETE'):
            return [AdminBearerAuthentication()]
        return []

    def get_permissions(self):
        if getattr(self, 'request', None) and self.request.method in ('PATCH', 'DELETE'):
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary='Бренд по id',
        description='GET без авторизации. UUID бренда.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(r.brand_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить бренд',
        description='PATCH только для админа (Bearer). Можно передать новое изображение.',
        request={'multipart/form-data': REQ_SERVICE_BRAND_PATCH},
    )
    async def patch(self, request, pk: str):
        _require_admin(request)
        return Response(await sync_to_async(r.brand_update)(str(pk), dict(request.data), request.FILES.get('image')))

    @extend_schema(
        summary='Удалить бренд',
        description='DELETE только для админа. Каскадное поведение зависит от моделей БД.',
    )
    async def delete(self, request, pk: str):
        _require_admin(request)
        await sync_to_async(r.brand_delete)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Ремонт — Модели'])
class ServiceModelRootView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Создать модель устройства для ремонта',
        description='JSON: привязка к бренду, название, slug и др. Ответ содержит id и slug.',
        request=REQ_SERVICE_MODEL_CREATE,
    )
    async def post(self, request):
        m = await sync_to_async(r.sm_create)(dict(request.data))
        return Response({'id': str(m.id), 'slug': m.slug})


@extend_schema(tags=['Ремонт — Модели'])
class ServiceModelPageView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список моделей (пагинация)',
        description='Параметры: `page`, `limit`. Каталог моделей для прайса и фильтров ремонта.',
    )
    async def get(self, request, page: int, limit: int):
        return Response(await sync_to_async(r.sm_page)(int(page), int(limit)))


@extend_schema(tags=['Ремонт — Модели'])
class ServiceModelSlugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Модель по slug',
        description='Публичная карточка модели по человекочитаемому URL.',
    )
    async def get(self, request, slug: str):
        data = await sync_to_async(r.sm_by_slug)(slug)
        if not data:
            raise NotFound()
        return Response(data)


@extend_schema(tags=['Ремонт — Модели'])
class ServiceModelDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Модель по id',
        description='UUID модели.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(r.sm_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить модель',
        description='Частичное обновление полей модели.',
        request=REQ_SERVICE_MODEL_PATCH,
    )
    async def patch(self, request, pk: str):
        return Response(await sync_to_async(r.sm_update)(str(pk), dict(request.data)))

    @extend_schema(
        summary='Удалить модель',
        description='Удаление записи модели.',
    )
    async def delete(self, request, pk: str):
        await sync_to_async(r.sm_delete)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Ремонт — Услуги'])
class ServiceRootView(APIView):
    authentication_classes = [AdminBearerAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Создать услугу ремонта',
        description='Только админ (Bearer). Ответ: id и slug услуги.',
        request=REQ_SERVICE_CREATE,
    )
    async def post(self, request):
        _require_admin(request)
        s = await sync_to_async(r.svc_create)(dict(request.data))
        return Response({'id': str(s.id), 'slug': s.slug})


@extend_schema(tags=['Ремонт — Услуги'])
class ServicePageView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список услуг (пагинация)',
        description='Параметры: `page`, `limit`. Публичный каталог услуг с ценами и привязками.',
    )
    async def get(self, request, page: int, limit: int):
        return Response(await sync_to_async(r.svc_page)(int(page), int(limit)))


@extend_schema(tags=['Ремонт — Услуги'])
class ServiceSlugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Услуга по slug',
        description='Детальная карточка услуги для страницы ремонта.',
    )
    async def get(self, request, slug: str):
        data = await sync_to_async(r.svc_by_slug)(slug)
        if not data:
            raise NotFound()
        return Response(data)


@extend_schema(tags=['Ремонт — Услуги'])
class ServiceDetailView(APIView):
    permission_classes = [AllowAny]

    def get_authenticators(self):
        if getattr(self, 'request', None) and self.request.method in ('PATCH', 'DELETE'):
            return [AdminBearerAuthentication()]
        return []

    def get_permissions(self):
        if getattr(self, 'request', None) and self.request.method in ('PATCH', 'DELETE'):
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary='Услуга по id',
        description='GET без авторизации.',
    )
    async def get(self, request, pk: str):
        row = await sync_to_async(r.svc_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    @extend_schema(
        summary='Обновить услугу',
        description='PATCH только для админа (Bearer).',
        request=REQ_SERVICE_PATCH,
    )
    async def patch(self, request, pk: str):
        _require_admin(request)
        return Response(await sync_to_async(r.svc_update)(str(pk), dict(request.data)))

    @extend_schema(
        summary='Удалить услугу',
        description='DELETE только для админа.',
    )
    async def delete(self, request, pk: str):
        _require_admin(request)
        await sync_to_async(r.svc_delete)(str(pk))
        return Response(status=204)

from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.common.views import APIView

from apps.catalog import dict_sync as d
from apps.common.openapi_requests import (
    REQ_BRAND_PATCH,
    REQ_BRAND_WRITE,
    REQ_CATEGORY_CREATE,
    REQ_CATEGORY_PATCH,
    REQ_COLOR_PATCH,
    REQ_COLOR_WRITE,
    REQ_CONDITION_PATCH,
    REQ_CONDITION_WRITE,
    REQ_MEMORY_PATCH,
    REQ_MEMORY_WRITE,
    REQ_PRODUCT_MODEL_PATCH,
    REQ_PRODUCT_MODEL_WRITE,
    REQ_SIMTYPE_PATCH,
    REQ_SIMTYPE_WRITE,
)


@extend_schema_view(
    get=extend_schema(
        summary='Список цветов',
        description='Возвращает все цвета из справочника. Используется для вариантов товара (ProductVariant).',
    ),
    post=extend_schema(
        summary='Создать цвет',
        description='Создаёт запись цвета. Поля JSON: `name` (обязательно), `hex` (опционально, HEX-код).',
        request=REQ_COLOR_WRITE,
    ),
)
@extend_schema(tags=['Справочники — Цвета'])
class ColorListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.color_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.color_create)(dict(request.data)))


@extend_schema_view(
    get=extend_schema(
        summary='Получить цвет по id',
        description='Возвращает одну запись справочника по числовому идентификатору.',
    ),
    patch=extend_schema(
        summary='Обновить цвет',
        description='Частичное обновление: можно передать `name` и/или `hex`.',
        request=REQ_COLOR_PATCH,
    ),
    delete=extend_schema(
        summary='Удалить цвет',
        description='Удаляет цвет. Убедитесь, что нет вариантов товара, ссылающихся на этот цвет.',
    ),
)
@extend_schema(tags=['Справочники — Цвета'])
class ColorDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: int):
        row = await sync_to_async(d.color_one)(int(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: int):
        return Response(await sync_to_async(d.color_update)(int(pk), dict(request.data)))

    async def delete(self, request, pk: int):
        await sync_to_async(d.color_delete)(int(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список объёмов памяти',
        description='Справочник памяти (например, 128 GB) для вариантов смартфонов и планшетов.',
    ),
    post=extend_schema(
        summary='Создать запись памяти',
        description='Поле `name` — отображаемое название объёма (обязательно).',
        request=REQ_MEMORY_WRITE,
    ),
)
@extend_schema(tags=['Справочники — Память'])
class MemoryListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.memory_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.memory_create)(dict(request.data)))


@extend_schema_view(
    get=extend_schema(summary='Память по id', description='Одна запись справочника по id.'),
    patch=extend_schema(summary='Обновить память', description='Поле `name` — новое название.', request=REQ_MEMORY_PATCH),
    delete=extend_schema(summary='Удалить память', description='Удаление записи по id.'),
)
@extend_schema(tags=['Справочники — Память'])
class MemoryDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: int):
        row = await sync_to_async(d.memory_one)(int(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: int):
        return Response(await sync_to_async(d.memory_update)(int(pk), dict(request.data)))

    async def delete(self, request, pk: int):
        await sync_to_async(d.memory_delete)(int(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список брендов',
        description='Все бренды техники, привязанные к товарам каталога.',
    ),
    post=extend_schema(
        summary='Создать бренд',
        description='Поле `name` — название бренда (обязательно). Файл формы: `image` (логотип, опционально).',
        request={'multipart/form-data': REQ_BRAND_WRITE},
    ),
)
@extend_schema(tags=['Справочники — Бренды'])
class BrandListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.brand_list)())

    async def post(self, request):
        return Response(
            await sync_to_async(d.brand_create)(dict(request.data), request.FILES.get('image'))
        )


@extend_schema_view(
    get=extend_schema(summary='Бренд по id', description='Одна запись бренда.'),
    patch=extend_schema(
        summary='Обновить бренд',
        description='JSON-поля и опционально файл `image` в multipart.',
        request={'multipart/form-data': REQ_BRAND_PATCH},
    ),
    delete=extend_schema(summary='Удалить бренд', description='Удаление бренда по id.'),
)
@extend_schema(tags=['Справочники — Бренды'])
class BrandDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: int):
        row = await sync_to_async(d.brand_one)(int(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: int):
        return Response(
            await sync_to_async(d.brand_update)(int(pk), dict(request.data), request.FILES.get('image'))
        )

    async def delete(self, request, pk: int):
        await sync_to_async(d.brand_delete)(int(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список категорий',
        description='Категории каталога (смартфоны, планшеты и т.д.) с иконкой и slug.',
    ),
    post=extend_schema(
        summary='Создать категорию',
        description='Поля: `name` (обязательно). Файл формы: `icon` (изображение категории, опционально).',
        request={'multipart/form-data': REQ_CATEGORY_CREATE},
    ),
)
@extend_schema(tags=['Справочники — Категории'])
class CategoryListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.category_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.category_create)(dict(request.data), request.FILES.get('icon')))


@extend_schema_view(
    get=extend_schema(
        summary='Заполнить slug категорий',
        description='Служебный метод: для всех категорий без slug генерирует slug из названия (как в Nest `GET /category/set-slug`).',
    ),
)
@extend_schema(tags=['Справочники — Категории'])
class CategorySetSlugView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        msg = await sync_to_async(d.category_set_slugs)()
        return Response(msg)


@extend_schema_view(
    get=extend_schema(summary='Категория по id', description='Одна категория с полями name, icon, slug.'),
    patch=extend_schema(
        summary='Обновить категорию',
        description='JSON-поля и опционально файл `icon` в multipart.',
        request={'multipart/form-data': REQ_CATEGORY_PATCH},
    ),
    delete=extend_schema(summary='Удалить категорию', description='Удаление категории по числовому id.'),
)
@extend_schema(tags=['Справочники — Категории'])
class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: int):
        row = await sync_to_async(d.category_one)(int(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: int):
        return Response(
            await sync_to_async(d.category_update)(int(pk), dict(request.data), request.FILES.get('icon'))
        )

    async def delete(self, request, pk: int):
        await sync_to_async(d.category_delete)(int(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список состояний товара',
        description='Справочник состояния (новый, б/у и т.д.) для фильтров и карточки товара.',
    ),
    post=extend_schema(
        summary='Создать состояние',
        description='Поле `name` — название состояния (обязательно). Идентификатор UUID генерируется автоматически.',
        request=REQ_CONDITION_WRITE,
    ),
)
@extend_schema(tags=['Справочники — Состояние'])
class ConditionListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.condition_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.condition_create)(dict(request.data)))


@extend_schema_view(
    get=extend_schema(summary='Состояние по id', description='Запись по UUID.'),
    patch=extend_schema(summary='Обновить состояние', description='Поле `name`.', request=REQ_CONDITION_PATCH),
    delete=extend_schema(summary='Удалить состояние', description='Удаление по UUID.'),
)
@extend_schema(tags=['Справочники — Состояние'])
class ConditionDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: str):
        row = await sync_to_async(d.condition_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: str):
        return Response(await sync_to_async(d.condition_update)(str(pk), dict(request.data)))

    async def delete(self, request, pk: str):
        await sync_to_async(d.condition_delete)(str(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список типов SIM',
        description='Типы SIM-карт для вариантов товара (одна SIM, eSIM и т.д.).',
    ),
    post=extend_schema(
        summary='Создать тип SIM',
        description='Поле `name` — уникальное название типа. id генерируется как UUID.',
        request=REQ_SIMTYPE_WRITE,
    ),
)
@extend_schema(tags=['Справочники — SIM'])
class SimTypeListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.simtype_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.simtype_create)(dict(request.data)))


@extend_schema_view(
    get=extend_schema(summary='Тип SIM по id', description='Одна запись по UUID.'),
    patch=extend_schema(summary='Обновить тип SIM', description='Поле `name` (уникальное).', request=REQ_SIMTYPE_PATCH),
    delete=extend_schema(summary='Удалить тип SIM', description='Удаление по UUID.'),
)
@extend_schema(tags=['Справочники — SIM'])
class SimTypeDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: str):
        row = await sync_to_async(d.simtype_one)(str(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: str):
        return Response(await sync_to_async(d.simtype_update)(str(pk), dict(request.data)))

    async def delete(self, request, pk: str):
        await sync_to_async(d.simtype_delete)(str(pk))
        return Response(status=204)


@extend_schema_view(
    get=extend_schema(
        summary='Список моделей каталога',
        description='Модельные ряды (например, серия смартфона), привязка к товарам через `modelId`.',
    ),
    post=extend_schema(
        summary='Создать модель',
        description='Поле `name` — название модели (обязательно).',
        request=REQ_PRODUCT_MODEL_WRITE,
    ),
)
@extend_schema(tags=['Справочники — Модели'])
class ProductModelListCreateView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request):
        return Response(await sync_to_async(d.product_model_list)())

    async def post(self, request):
        return Response(await sync_to_async(d.product_model_create)(dict(request.data)))


@extend_schema_view(
    get=extend_schema(summary='Модель по id', description='Одна запись ProductModel.'),
    patch=extend_schema(summary='Обновить модель', description='Поле `name`.', request=REQ_PRODUCT_MODEL_PATCH),
    delete=extend_schema(summary='Удалить модель', description='Удаление по числовому id.'),
)
@extend_schema(tags=['Справочники — Модели'])
class ProductModelDetailView(APIView):
    permission_classes = [AllowAny]

    async def get(self, request, pk: int):
        row = await sync_to_async(d.product_model_one)(int(pk))
        if not row:
            raise NotFound()
        return Response(row)

    async def patch(self, request, pk: int):
        return Response(await sync_to_async(d.product_model_update)(int(pk), dict(request.data)))

    async def delete(self, request, pk: int):
        await sync_to_async(d.product_model_delete)(int(pk))
        return Response(status=204)

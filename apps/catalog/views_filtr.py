from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog import filtr_sync
from apps.common.openapi_requests import REQ_FILTR_CATALOG


@extend_schema(tags=['Фильтры — Отбор'])
class FiltrPostView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Фильтрация каталога',
        description=(
            'POST с телом в формате Nest `filtr`: критерии по категории, бренду, модели, цене, памяти, цвету, '
            'состоянию, SIM и т.д. Возвращает отфильтрованный список товаров с вариантами. '
            'Схема ниже — типовые поля; дополнительные ключи Nest также допустимы.'
        ),
        request=REQ_FILTR_CATALOG,
    )
    async def post(self, request):
        data = await sync_to_async(filtr_sync.filter_products)(dict(request.data))
        return Response(data)


@extend_schema(tags=['Фильтры — Справочники'])
class FiltrFilterDataView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Справочник значений для фильтров',
        description=(
            'Путь: slug категории. Опциональные query: `modelId`, `brandId` — сужают набор доступных опций '
            '(диапазоны цен, память, цвета и пр.) для построения UI фильтров.'
        ),
    )
    async def get(self, request, slug: str):
        model_id = request.query_params.get('modelId')
        brand_id = request.query_params.get('brandId')
        m_id = int(model_id) if model_id and str(model_id).isdigit() else None
        b_id = int(brand_id) if brand_id and str(brand_id).isdigit() else None
        data = await sync_to_async(filtr_sync.get_filter_data)(slug, m_id, b_id)
        return Response(data)


@extend_schema(tags=['Фильтры — Справочники'])
class FiltrBrandsModelsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Бренды и модели в категории',
        description='Параметр пути: числовой id категории. Возвращает дерево брендов с привязанными моделями для фильтра или навигации.',
    )
    async def get(self, request, category_id: int):
        data = await sync_to_async(filtr_sync.get_brands_and_models_by_category)(int(category_id))
        return Response(data)


@extend_schema(tags=['Фильтры — Подборки'])
class FiltrBestOffersView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Подборки витрины',
        description=(
            'Готовые блоки: товары со скидкой, хиты, новинки, б/у (лимит по умолчанию 8 на блок). '
            'Используется главной и маркетинговыми секциями.'
        ),
    )
    async def get(self, request):
        data = await sync_to_async(filtr_sync.get_best_offers)(8)
        return Response(data)


@extend_schema(tags=['Фильтры — Справочники'])
class FiltrIsHasProductView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Проверка slug товара',
        description='Возвращает признак, существует ли товар с данным slug (например, перед редиректом на карточку).',
    )
    async def get(self, request, slug: str):
        ok = await sync_to_async(filtr_sync.is_has_product)(slug)
        return Response(ok)


@extend_schema(tags=['Фильтры — SIM'])
class FiltrCleanSimView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Служебная очистка SIM (совместимость)',
        description='Эндпоинт из Nest для массовой правки связей simType у вариантов. Обычно не вызывается с фронтенда.',
    )
    async def get(self, request):
        msg = await sync_to_async(filtr_sync.clean_all_sim_type_id_products)()
        return Response(msg)


@extend_schema(tags=['Фильтры — SIM'])
class FiltrBySimtypeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Товары по типу SIM',
        description='UUID типа SIM в пути. Возвращает товары, у которых у варианта выбран этот тип (одиночная FK на варианте).',
    )
    async def get(self, request, simtype_id: str):
        data = await sync_to_async(filtr_sync.filtr_by_variant_sim_type_products)(simtype_id)
        return Response(data)

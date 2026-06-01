from __future__ import annotations

from asgiref.sync import sync_to_async
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from apps.common.views import APIView

from apps.common.authentication import AdminBearerAuthentication, CookieJWTAuthentication, StoreAdminPrincipal, StoreUserPrincipal
from apps.common.integrations.telegram import telegram_send_markdown
from apps.storefront import storefront_sync as sf
from apps.storefront.models import Review


def _require_user(request) -> str:
    if not isinstance(request.user, StoreUserPrincipal):
        raise PermissionDenied('Требуется авторизация (cookie access_token)')
    return request.user.pk


def _require_admin(request) -> None:
    if not isinstance(request.user, StoreAdminPrincipal):
        raise PermissionDenied()


@extend_schema(tags=['Избранное'])
class FavoriteRootView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Список избранного',
        description='Требуется cookie `access_token`. Возвращает карточки товаров (вариант + цена + изображение).',
    )
    async def get(self, request):
        uid = _require_user(request)
        data = await sync_to_async(sf.list_favorites)(uid)
        return Response(data)

    @extend_schema(
        summary='Добавить в избранное',
        description='JSON: `variantId` (UUID варианта ProductVariant).',
    )
    async def post(self, request):
        uid = _require_user(request)
        vid = (request.data.get('variantId') or request.data.get('variant_id') or '').strip()
        if not vid:
            raise ValidationError('variantId обязателен')
        try:
            card = await sync_to_async(sf.add_favorite)(uid, vid)
        except LookupError as e:
            raise NotFound(str(e)) from e
        return Response(card)


@extend_schema(tags=['Избранное'])
class FavoriteDetailView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Удалить из избранного',
        description='UUID варианта в пути.',
    )
    async def delete(self, request, variant_id: str):
        uid = _require_user(request)
        await sync_to_async(sf.remove_favorite)(uid, str(variant_id))
        return Response(status=204)


@extend_schema(tags=['Корзина'])
class CartRootView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Содержимое корзины',
        description='Список позиций с количеством, суммой по строке и общим `totalPrice`.',
    )
    async def get(self, request):
        uid = _require_user(request)
        return Response(await sync_to_async(sf.list_cart)(uid))

    @extend_schema(
        summary='Добавить в корзину',
        description='JSON: `variantId`, опционально `quantity` (по умолчанию 1). Если позиция уже есть — количество увеличивается.',
    )
    async def post(self, request):
        uid = _require_user(request)
        vid = (request.data.get('variantId') or request.data.get('variant_id') or '').strip()
        qty = int(request.data.get('quantity') or 1)
        if not vid:
            raise ValidationError('variantId обязателен')
        try:
            data = await sync_to_async(sf.add_cart_item)(uid, vid, qty)
        except LookupError as e:
            raise NotFound(str(e)) from e
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(data)

    @extend_schema(
        summary='Очистить корзину',
        description='Удаляет все позиции пользователя.',
    )
    async def delete(self, request):
        uid = _require_user(request)
        return Response(await sync_to_async(sf.clear_cart)(uid))


@extend_schema(tags=['Корзина'])
class CartItemView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Изменить количество',
        description='PATCH JSON: `quantity` (>= 1).',
    )
    async def patch(self, request, variant_id: str):
        uid = _require_user(request)
        qty = int(request.data.get('quantity') or 0)
        try:
            data = await sync_to_async(sf.update_cart_quantity)(uid, str(variant_id), qty)
        except LookupError as e:
            raise NotFound(str(e)) from e
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(data)

    @extend_schema(
        summary='Удалить позицию из корзины',
        description='UUID варианта в пути.',
    )
    async def delete(self, request, variant_id: str):
        uid = _require_user(request)
        return Response(await sync_to_async(sf.remove_cart_item)(uid, str(variant_id)))


@extend_schema(tags=['Отзывы'])
class ReviewRootView(APIView):
    authentication_classes = [AdminBearerAuthentication]

    def get_permissions(self):
        if getattr(self, 'request', None) and self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary='Список отзывов',
        description='Query: `page`, `limit`, `source` (`all` | `avito` | `yandex` | `site`). Для страницы «Отзывы» в Figma.',
    )
    async def get(self, request):
        page = max(1, int(request.query_params.get('page') or 1))
        limit = min(60, max(1, int(request.query_params.get('limit') or 10)))
        source = (request.query_params.get('source') or 'all').strip().lower()
        data = await sync_to_async(sf.list_reviews)(page, limit, source)
        return Response(data)

    @extend_schema(
        summary='Создать отзыв (админ)',
        description='Bearer admin JWT. Поля: authorName, text, rating, source, videoUrl, thumbnail, isPublished.',
    )
    async def post(self, request):
        _require_admin(request)
        if not request.data.get('authorName'):
            raise ValidationError('authorName обязателен')
        out = await sync_to_async(sf.create_review)(dict(request.data))
        return Response(out)


@extend_schema(tags=['Отзывы'])
class ReviewVideoListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Видео-отзывы',
        description='Query: `page`, `limit`. Только записи с заполненным `videoUrl`.',
    )
    async def get(self, request):
        page = max(1, int(request.query_params.get('page') or 1))
        limit = min(60, max(1, int(request.query_params.get('limit') or 8)))
        return Response(await sync_to_async(sf.list_video_reviews)(page, limit))


@extend_schema(tags=['Отзывы'])
class ReviewDetailView(APIView):
    authentication_classes = [AdminBearerAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Обновить отзыв (админ)')
    async def patch(self, request, pk: str):
        _require_admin(request)
        try:
            out = await sync_to_async(sf.update_review)(str(pk), dict(request.data))
        except Review.DoesNotExist as e:
            raise NotFound() from e
        return Response(out)

    @extend_schema(summary='Удалить отзыв (админ)')
    async def delete(self, request, pk: str):
        _require_admin(request)
        await sync_to_async(sf.delete_review)(str(pk))
        return Response(status=204)


@extend_schema(tags=['Сайт — Настройки'])
class SiteSettingsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Контакты и блоки главной',
        description=(
            'Телефон, email, адрес, соцсети, координаты карты, блок «Наши преимущества», '
            'список категорий для футера/каталога. Редактируется в Django Admin → «Настройки сайта».'
        ),
    )
    async def get(self, request):
        return Response(await sync_to_async(sf.get_site_settings)())


@extend_schema(tags=['Заявки'])
class ConsultationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Заявка «Получить консультацию»',
        description='JSON: `name`, `phone`, опционально `consent`. Уведомление в Telegram (как форма Help).',
    )
    async def post(self, request):
        d = dict(request.data)
        name = (d.get('name') or '').strip()
        phone = (d.get('phone') or '').strip()
        if not name or not phone:
            raise ValidationError('name и phone обязательны')
        text = (
            f'📞 *Заявка на консультацию (с сайта)*\n\n'
            f'👤 *Имя:* {name}\n'
            f'📱 *Телефон:* {phone}\n'
            f'✅ *Согласие:* {"Да" if d.get("consent") else "Нет"}'
        )
        await telegram_send_markdown(text)
        return Response({'message': 'Заявка успешно отправлена'})


@extend_schema(tags=['Товары — Витрина'])
class ProductSearchSuggestView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Подсказки поиска (как в Figma)',
        description='Путь: строка запроса. Ответ: `products` (карточки) и `tags` (быстрые фильтры).',
    )
    async def get(self, request, query: str):
        limit = min(20, max(1, int(request.query_params.get('limit') or 8)))
        return Response(await sync_to_async(sf.search_suggest)(query, limit))


@extend_schema(tags=['Товары — Витрина'])
class ProductRelatedView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Похожие / «С этим покупают»',
        description='Товары той же категории (кроме текущего). Query `limit` (по умолчанию 4).',
    )
    async def get(self, request, slug: str):
        limit = min(20, max(1, int(request.query_params.get('limit') or 4)))
        data = await sync_to_async(sf.related_products)(slug, limit)
        return Response(data)


@extend_schema(tags=['Блог — Статьи'])
class BlogRelatedView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Другие новости',
        description='Для блока «Другие новости» на странице статьи. Query `limit` (по умолчанию 3).',
    )
    async def get(self, request, slug: str):
        limit = min(10, max(1, int(request.query_params.get('limit') or 3)))
        return Response(await sync_to_async(sf.related_blogs)(slug, limit))

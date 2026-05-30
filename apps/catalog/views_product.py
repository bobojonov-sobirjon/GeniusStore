from __future__ import annotations

import json

from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog import product_sync
from apps.catalog.serialization import product_to_dict
from apps.common.integrations.telegram import telegram_send_markdown
from apps.common.openapi_requests import (
    REQ_HELP_FORM,
    REQ_ORDER_CART,
    REQ_ORDER_ONE,
    REQ_ORDER_USER,
    REQ_PRODUCT_CREATE,
    REQ_PRODUCT_PATCH,
    REQ_PRODUCT_VARIANT_PATCH,
    REQ_QUICK_ORDER,
    REQ_REPAIR_FORM,
    REQ_TRADEIN_FORM,
)
from apps.store_core.models import StoreOrder, StoreUser


async def _mail(subject: str, body: str, to_list: list[str]):
    await sync_to_async(send_mail)(
        subject,
        body,
        None,
        to_list,
        fail_silently=True,
    )


def _help_text(d: dict) -> str:
    return (
        f'📩 *Новая заявка с сайта*\n'
        f'👤 Имя: {d.get("name")}\n'
        f'📞 Телефон: {d.get("phone")}\n'
        f'✅ Согласие: {"Да" if d.get("consent") else "Нет"}'
    )


def _tradein_text(d: dict) -> str:
    return (
        f'🔄 *НОВАЯ ЗАЯВКА TRADE-IN*\n\n'
        f'👤 *Имя:* {d.get("name")}\n'
        f'📞 *Телефон:* {d.get("phone")}\n'
        f'📱 *Старое устройство:* {d.get("oldDevice") or "Не указано"}\n\n'
        f'🛍️ *Интересует товар:* \n   {d.get("productTitle") or "Не указан"}'
    )


def _repair_text(d: dict) -> str:
    serviced = d.get('previouslyServiced')
    serviced_t = 'Да' if serviced == 'yes' else 'Нет' if serviced == 'no' else 'Не указано'
    return (
        f'🛠 *Заявка на ремонт (с сайта)*\n\n'
        f'👤 *Имя:* {d.get("name")}\n'
        f'📞 *Телефон:* {d.get("phone")}\n\n'
        f'📱 *Модель:* {d.get("model")}\n'
        f'📝 *Проблема:* {d.get("problem")}\n\n'
        f'🔁 *Ранее в сервис:* {serviced_t}\n'
        f'✅ *Согласие:* {"Да" if d.get("agreeToPrivacy") else "Нет"}'
    )


@extend_schema(tags=['Товары — Управление'])
class ProductCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Создание товара (multipart)',
        description=(
            'Создаёт товар и варианты. Поля формы как в Nest: title, brandId, categoryId, conditionId, modelId, '
            'характеристики, флаги isNew/isHit/isBt, массив `variants` (JSON-строка или массив) с memoryId, colorId, price, '
            'simTypes и т.д. Файлы имён `variant_{индекс}_image_{номер}` прикрепляются к соответствующему варианту. '
            'Slug генерируется из названия.'
        ),
        request={'multipart/form-data': REQ_PRODUCT_CREATE},
    )
    async def post(self, request):
        try:
            p = await sync_to_async(product_sync.create_product)(dict(request.data), request.FILES)
        except Exception as e:
            raise ValidationError(str(e)) from e
        return Response(product_to_dict(p))


@extend_schema(tags=['Заявки'])
class ProductHelpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Форма обратной связи «Помощь»',
        description=(
            'Дублирует заявку в Telegram (если заданы TELEGRAM_*) '
            'и отправляет простое письмо на info@whalestore.ru.'
        ),
        request=REQ_HELP_FORM,
    )
    async def post(self, request):
        d = dict(request.data)
        await telegram_send_markdown(_help_text(d))
        html = f"<p>{d.get('name')}</p><p>{d.get('phone')}</p>"
        await _mail('Новая заявка с формы Help', html, ['info@whalestore.ru'])
        return Response({'message': 'Заявка успешно отправлена'})


@extend_schema(tags=['Заявки'])
class ProductTradeInView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Заявка Trade-in',
        description='Уведомление уходит в Telegram.',
        request=REQ_TRADEIN_FORM,
    )
    async def post(self, request):
        d = dict(request.data)
        await telegram_send_markdown(_tradein_text(d))
        return Response({'ok': True})


@extend_schema(tags=['Заявки'])
class ProductRepairView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Заявка на ремонт',
        description=(
            'Сообщение формируется в Markdown и отправляется в Telegram.'
        ),
        request=REQ_REPAIR_FORM,
    )
    async def post(self, request):
        d = dict(request.data)
        await telegram_send_markdown(_repair_text(d))
        return Response({'ok': True})


@extend_schema(tags=['Заказы'])
class ProductOrder2View(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Оформление заказа с привязкой к пользователю',
        description=(
            'Путь содержит `userId` (UUID). Создаётся запись в таблице Order; отправляется письмо клиенту и копия на info@whalestore.ru.'
        ),
        request=REQ_ORDER_USER,
    )
    async def post(self, request, user_id: str):
        body = dict(request.data)
        user = await sync_to_async(lambda: StoreUser.objects.filter(pk=user_id).first())()
        if not user:
            raise NotFound('Пользователь не найден')
        order = await sync_to_async(
            lambda: StoreOrder.objects.create(
                user_id=user_id,
                products=body.get('products') or [],
                total_sum=int(body.get('totalPrice') or 0),
            )
        )()
        await _mail(
            'Новый заказ',
            json.dumps(body, ensure_ascii=False, default=str),
            [body.get('email') or user.email, 'info@whalestore.ru'],
        )
        return Response({'id': str(order.id), 'totalSum': order.total_sum})


@extend_schema(tags=['Заказы'])
class ProductOrder4View(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Корзинный заказ (уведомление в Telegram и почту)',
        description=(
            'Соответствует Nest `send-order4`: краткое сообщение в Telegram и письмо с JSON тела на info@whalestore.ru.'
        ),
        request=REQ_ORDER_CART,
    )
    async def post(self, request):
        body = dict(request.data)
        text = f'Новый заказ: {body.get("fio")} {body.get("phone")} на {body.get("totalPrice")}'
        await telegram_send_markdown(text)
        await _mail('Новый заказ', json.dumps(body, ensure_ascii=False, default=str), ['info@whalestore.ru'])
        return Response({'message': 'Order email sent successfully'})


@extend_schema(tags=['Заказы'])
class ProductOrder3View(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Заказ одной позиции для авторизованного пользователя',
        description='userId в пути. Создаётся Order и письмо на email пользователя.',
        request=REQ_ORDER_ONE,
    )
    async def post(self, request, user_id: str):
        body = dict(request.data)
        user = await sync_to_async(lambda: StoreUser.objects.filter(pk=user_id).first())()
        if not user:
            raise NotFound('Пользователь не найден')
        product = body.get('product')
        total = int(body.get('totalPrice') or 0)
        order = await sync_to_async(
            lambda: StoreOrder.objects.create(user_id=user_id, products=[product], total_sum=total)
        )()
        await _mail('Подтверждение заказа', str(product), [user.email])
        return Response({'id': str(order.id)})


@extend_schema(tags=['Заказы'])
class ProductQuickOrderView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Быстрый заказ без регистрации',
        description=(
            'Письмо с данными на указанный email. Ответ 204 без тела при успехе.'
        ),
        request=REQ_QUICK_ORDER,
    )
    async def post(self, request):
        body = dict(request.data)
        await _mail('Быстрый заказ', json.dumps(body, ensure_ascii=False, default=str), [body.get('email')])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Товары — Витрина'])
class ProductSearchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Поиск товаров по строке',
        description='Параметр пути `query` — подстрока без учёта регистра в полях title и description. Возвращает массив товаров с вариантами.',
    )
    async def get(self, request, query: str):
        data = await sync_to_async(product_sync.search_products)(query)
        return Response(data)


@extend_schema(tags=['Товары — Витрина'])
class ProductListPagedView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Список всех товаров с пагинацией',
        description='Параметры пути: `page`, `limit` (1-based страница). Возвращает `{ data, count }` — count в текущей реализации — длина страницы (как упрощение Nest).',
    )
    async def get(self, request, page: int, limit: int):
        data = await sync_to_async(product_sync.list_products_page)(int(page), int(limit))
        return Response(data)


@extend_schema(tags=['Товары — Витрина'])
class ProductByCategorySlugView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Товары категории по slug',
        description='Путь: slug категории, затем page и limit. Ответ включает `data`, `category`, `count` — блок категории для шапки витрины.',
    )
    async def get(self, request, slug: str, page: int, limit: int):
        data = await sync_to_async(product_sync.list_products_category_slug)(int(page), int(limit), slug)
        return Response(data)


@extend_schema(tags=['Товары — Витрина'])
class ProductByCategoryIdView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Товары категории по числовому id',
        description='Параметры: categoryId, page, limit. Возвращает `{ data, count }` с полными вложениями вариантов.',
    )
    async def get(self, request, category_id: int, page: int, limit: int):
        data = await sync_to_async(product_sync.list_products_category_id)(int(page), int(limit), int(category_id))
        return Response(data)


@extend_schema(tags=['Товары — Витрина'])
class ProductSlugDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Карточка товара по slug',
        description='Уникальный slug товара. Возвращает товар с brand, category, condition, model и массивом variants (память, цвет, simTypes).',
    )
    async def get(self, request, slug: str):
        data = await sync_to_async(product_sync.get_product_by_slug)(slug)
        if not data:
            raise NotFound()
        return Response(data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Товары — Витрина'],
        summary='Карточка товара по числовому id',
        description='Полный объект товара как в Nest (бренд, категория, варианты и т.д.).',
    )
    async def get(self, request, pk: int):
        data = await sync_to_async(product_sync.get_product)(int(pk))
        if not data:
            raise NotFound()
        return Response(data)

    @extend_schema(
        tags=['Товары — Управление'],
        summary='Обновление товара',
        description='Логика как при создании: поля товара, JSON variants, файлы variant_i_image_j.',
        request={'multipart/form-data': REQ_PRODUCT_PATCH},
    )
    async def patch(self, request, pk: int):
        p = await sync_to_async(product_sync.update_product)(int(pk), dict(request.data), request.FILES)
        return Response(product_to_dict(p))

    @extend_schema(
        tags=['Товары — Управление'],
        summary='Удаление товара',
        description='Сначала удаляются все ProductVariant, затем сам Product.',
    )
    async def delete(self, request, pk: int):
        await sync_to_async(product_sync.delete_product)(int(pk))
        return Response(status=204)


@extend_schema(tags=['Товары — Варианты'])
class ProductVariantPatchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Частичное обновление варианта товара',
        description=(
            'UUID варианта в пути. Пересоздаётся таблица связей sim-типов при передаче simTypes.'
        ),
        request=REQ_PRODUCT_VARIANT_PATCH,
    )
    async def patch(self, request, variant_id: str):
        try:
            data = await sync_to_async(product_sync.update_variant)(str(variant_id), dict(request.data))
        except Exception as e:
            raise ValidationError(str(e)) from e
        return Response(data)


@extend_schema(tags=['Товары — Варианты'])
class ProductVariantDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Удаление варианта товара',
        description='Путь `.../variant/remove/{variant_id}` — удаляет строку ProductVariant (каскадно связанные sim-цены).',
    )
    async def delete(self, request, variant_id: str):
        await sync_to_async(product_sync.delete_variant)(str(variant_id))
        return Response(status=204)


@extend_schema(tags=['Товары — Варианты'])
class ProductVariantImageDeleteView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Удаление изображения из JSON-массива варианта',
        description='Удаляет элемент с `id` из поля images у варианта (UUID варианта и UUID картинки в пути).',
    )
    async def delete(self, request, variant_id: str, image_id: str):
        try:
            out = await sync_to_async(product_sync.remove_variant_image)(str(variant_id), str(image_id))
        except LookupError as e:
            raise NotFound(str(e)) from e
        return Response(out)

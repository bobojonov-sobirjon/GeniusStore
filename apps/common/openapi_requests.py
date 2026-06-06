"""
Сериализаторы только для документации OpenAPI (request body в Swagger / Redoc).
Не используются для валидации входящих данных в рантайме.
"""
from __future__ import annotations

from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

# --- Авторизация и пользователи ---
REQ_ADMIN_LOGIN = inline_serializer(
    name='AdminLoginRequest',
    fields={
        'username': serializers.CharField(help_text='Логин администратора'),
        'password': serializers.CharField(help_text='Пароль'),
    },
)

REQ_USER_REGISTER_JSON = inline_serializer(
    name='UserRegisterJsonRequest',
    fields={
        'email': serializers.EmailField(help_text='Обязательно'),
        'password': serializers.CharField(help_text='Обязательно'),
        'firstName': serializers.CharField(required=False, allow_blank=True),
        'lastName': serializers.CharField(required=False, allow_blank=True),
        'middleName': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_USER_REGISTER_MULTIPART = inline_serializer(
    name='UserRegisterMultipartRequest',
    fields={
        'email': serializers.EmailField(),
        'password': serializers.CharField(),
        'firstName': serializers.CharField(required=False, allow_blank=True),
        'lastName': serializers.CharField(required=False, allow_blank=True),
        'middleName': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'avatar': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_USER_PROFILE_PATCH_JSON = inline_serializer(
    name='UserProfilePatchJsonRequest',
    fields={
        'firstName': serializers.CharField(required=False, allow_blank=True),
        'lastName': serializers.CharField(required=False, allow_blank=True),
        'middleName': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.EmailField(required=False, allow_null=True),
        'password': serializers.CharField(required=False, allow_blank=True, help_text='Новый пароль'),
    },
)

REQ_USER_PROFILE_PATCH_MULTIPART = inline_serializer(
    name='UserProfilePatchMultipartRequest',
    fields={
        'firstName': serializers.CharField(required=False, allow_blank=True),
        'lastName': serializers.CharField(required=False, allow_blank=True),
        'middleName': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.EmailField(required=False, allow_null=True),
        'password': serializers.CharField(required=False, allow_blank=True),
        'avatar': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_USER_LOGIN = inline_serializer(
    name='UserLoginRequest',
    fields={
        'email': serializers.EmailField(),
        'password': serializers.CharField(),
    },
)

REQ_USER_RESET_PASSWORD = inline_serializer(
    name='UserResetPasswordRequest',
    fields={
        'emailOrUsername': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.CharField(required=False, allow_blank=True, help_text='Альтернатива emailOrUsername'),
    },
)

REQ_USER_AVATAR = inline_serializer(
    name='UserAvatarRequest',
    fields={
        'avatar': serializers.ImageField(help_text='Файл изображения'),
    },
)

REQ_ADMIN_CREATE = inline_serializer(
    name='AdminCreateRequest',
    fields={
        'username': serializers.CharField(),
        'password': serializers.CharField(),
    },
)

# --- Блог ---
REQ_BLOG_CATEGORY_WRITE = inline_serializer(
    name='BlogCategoryWriteRequest',
    fields={
        'name': serializers.CharField(),
    },
)

REQ_BLOG_CREATE_JSON = inline_serializer(
    name='BlogCreateJsonRequest',
    fields={
        'title': serializers.CharField(),
        'content': serializers.CharField(),
        'blogCategoryId': serializers.UUIDField(),
    },
)

REQ_BLOG_CREATE_MULTIPART = inline_serializer(
    name='BlogCreateMultipartRequest',
    fields={
        'title': serializers.CharField(),
        'content': serializers.CharField(),
        'blogCategoryId': serializers.UUIDField(),
        'image': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_BLOG_PATCH_JSON = inline_serializer(
    name='BlogPatchJsonRequest',
    fields={
        'title': serializers.CharField(required=False, allow_blank=True),
        'content': serializers.CharField(required=False, allow_blank=True),
        'blogCategoryId': serializers.UUIDField(required=False, allow_null=True),
    },
)

REQ_BLOG_PATCH_MULTIPART = inline_serializer(
    name='BlogPatchMultipartRequest',
    fields={
        'title': serializers.CharField(required=False, allow_blank=True),
        'content': serializers.CharField(required=False, allow_blank=True),
        'blogCategoryId': serializers.UUIDField(required=False, allow_null=True),
        'image': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_BLOG_STEPS_WRITE = inline_serializer(
    name='BlogStepsWriteRequest',
    fields={
        'title': serializers.CharField(),
        'content': serializers.CharField(),
        'blogId': serializers.UUIDField(help_text='UUID статьи (только при создании)'),
    },
)

REQ_BLOG_STEPS_PATCH = inline_serializer(
    name='BlogStepsPatchRequest',
    fields={
        'title': serializers.CharField(required=False, allow_blank=True),
        'content': serializers.CharField(required=False, allow_blank=True),
    },
)

# --- Сайт ---
REQ_BANNER_CREATE = inline_serializer(
    name='BannerCreateRequest',
    fields={
        'title': serializers.CharField(),
        'description': serializers.CharField(),
        'imgPc': serializers.ImageField(required=False, allow_null=True),
        'imgMobile': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_BANNER_PATCH = inline_serializer(
    name='BannerPatchRequest',
    fields={
        'title': serializers.CharField(required=False, allow_blank=True),
        'description': serializers.CharField(required=False, allow_blank=True),
        'imgPc': serializers.ImageField(required=False, allow_null=True),
        'imgMobile': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_INFO_WRITE = inline_serializer(
    name='InfoWriteRequest',
    fields={
        'name': serializers.CharField(),
        'description': serializers.CharField(required=False, allow_blank=True, allow_null=True),
    },
)

REQ_INFO_PATCH = inline_serializer(
    name='InfoPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'description': serializers.CharField(required=False, allow_blank=True, allow_null=True),
    },
)

# --- Ремонт ---
REQ_SERVICE_BRAND_CREATE = inline_serializer(
    name='ServiceBrandCreateRequest',
    fields={
        'name': serializers.CharField(),
        'image': serializers.ImageField(help_text='Обязательный файл изображения'),
    },
)

REQ_SERVICE_BRAND_PATCH = inline_serializer(
    name='ServiceBrandPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'image': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_SERVICE_MODEL_CREATE = inline_serializer(
    name='ServiceModelCreateRequest',
    fields={
        'name': serializers.CharField(),
        'serviceBrandId': serializers.UUIDField(required=False, allow_null=True, help_text='UUID бренда сервиса'),
    },
)

REQ_SERVICE_MODEL_PATCH = inline_serializer(
    name='ServiceModelPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_SERVICE_CREATE = inline_serializer(
    name='ServiceCreateRequest',
    fields={
        'name': serializers.CharField(),
        'laborOnly': serializers.IntegerField(help_text='Цена только работа'),
        'laborWithPart': serializers.IntegerField(help_text='Цена работа + запчасть'),
        'serviceModelId': serializers.UUIDField(required=False, allow_null=True),
    },
)

REQ_SERVICE_PATCH = inline_serializer(
    name='ServicePatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'laborOnly': serializers.IntegerField(required=False),
        'laborWithPart': serializers.IntegerField(required=False),
        'serviceModelId': serializers.UUIDField(required=False, allow_null=True),
    },
)

# --- Справочники каталога ---
REQ_COLOR_WRITE = inline_serializer(
    name='ColorWriteRequest',
    fields={
        'name': serializers.CharField(),
        'hex': serializers.CharField(required=False, allow_blank=True, allow_null=True),
    },
)

REQ_COLOR_PATCH = inline_serializer(
    name='ColorPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'hex': serializers.CharField(required=False, allow_blank=True, allow_null=True),
    },
)

REQ_MEMORY_WRITE = inline_serializer(
    name='MemoryWriteRequest',
    fields={'name': serializers.CharField()},
)

REQ_MEMORY_PATCH = inline_serializer(
    name='MemoryPatchRequest',
    fields={'name': serializers.CharField(required=False, allow_blank=True)},
)

REQ_BRAND_WRITE = inline_serializer(
    name='BrandWriteRequest',
    fields={
        'name': serializers.CharField(),
        'image': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_BRAND_PATCH = inline_serializer(
    name='BrandPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'image': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_CATEGORY_CREATE = inline_serializer(
    name='CategoryCreateRequest',
    fields={
        'name': serializers.CharField(),
        'icon': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_CATEGORY_PATCH = inline_serializer(
    name='CategoryPatchRequest',
    fields={
        'name': serializers.CharField(required=False, allow_blank=True),
        'icon': serializers.ImageField(required=False, allow_null=True),
    },
)

REQ_CONDITION_WRITE = inline_serializer(
    name='ConditionWriteRequest',
    fields={'name': serializers.CharField()},
)

REQ_CONDITION_PATCH = inline_serializer(
    name='ConditionPatchRequest',
    fields={'name': serializers.CharField(required=False, allow_blank=True)},
)

REQ_SIMTYPE_WRITE = inline_serializer(
    name='SimTypeWriteRequest',
    fields={'name': serializers.CharField(help_text='Уникальное название')},
)

REQ_SIMTYPE_PATCH = inline_serializer(
    name='SimTypePatchRequest',
    fields={'name': serializers.CharField(required=False, allow_blank=True)},
)

REQ_PRODUCT_MODEL_WRITE = inline_serializer(
    name='ProductModelWriteRequest',
    fields={'name': serializers.CharField()},
)

REQ_PRODUCT_MODEL_PATCH = inline_serializer(
    name='ProductModelPatchRequest',
    fields={'name': serializers.CharField(required=False, allow_blank=True)},
)

# --- Фильтр каталога (гибкое тело как в Nest) ---
REQ_FILTR_CATALOG = inline_serializer(
    name='FiltrCatalogRequest',
    fields={
        'categoryId': serializers.IntegerField(required=False, help_text='ID категории (альтернатива slug)'),
        'slug': serializers.CharField(required=False, allow_blank=True, help_text='Slug категории, напр. smartphones'),
        'brands': serializers.ListField(child=serializers.IntegerField(), required=False, help_text='[1, 2] — id брендов'),
        'brandId': serializers.IntegerField(required=False, help_text='Один бренд (alias)'),
        'models': serializers.ListField(child=serializers.IntegerField(), required=False),
        'modelId': serializers.IntegerField(required=False),
        'conditions': serializers.ListField(child=serializers.CharField(), required=False, help_text='UUID состояний'),
        'conditionIds': serializers.ListField(child=serializers.CharField(), required=False),
        'minPrice': serializers.FloatField(required=False),
        'maxPrice': serializers.FloatField(required=False),
        'memoryIds': serializers.ListField(child=serializers.IntegerField(), required=False, help_text='[1, 3] — id памяти (Memory)'),
        'memories': serializers.ListField(child=serializers.IntegerField(), required=False),
        'memoryId': serializers.IntegerField(required=False, help_text='Один id памяти, напр. 1'),
        'colors': serializers.ListField(child=serializers.IntegerField(), required=False),
        'colorIds': serializers.ListField(child=serializers.IntegerField(), required=False),
        'simTypes': serializers.ListField(child=serializers.CharField(), required=False, help_text='UUID типов SIM'),
        'simTypeIds': serializers.ListField(child=serializers.CharField(), required=False),
        'inStock': serializers.BooleanField(required=False, help_text='Только в наличии'),
        'isBt': serializers.BooleanField(required=False),
        'isAll': serializers.BooleanField(required=False, help_text='true — игнорировать фильтры'),
    },
)

# --- Товары и заказы ---
REQ_PRODUCT_CREATE = inline_serializer(
    name='ProductCreateMultipartRequest',
    fields={
        'title': serializers.CharField(),
        'brandId': serializers.IntegerField(),
        'categoryId': serializers.IntegerField(),
        'conditionId': serializers.UUIDField(required=False, allow_null=True),
        'modelId': serializers.IntegerField(required=False, allow_null=True),
        'variants': serializers.CharField(
            help_text='JSON-строка или массив: memoryId, colorId, price, simTypes и т.д.',
            required=False,
            allow_blank=True,
        ),
        'isNew': serializers.BooleanField(required=False),
        'isHit': serializers.BooleanField(required=False),
        'isBt': serializers.BooleanField(required=False),
        'article': serializers.CharField(required=False, allow_blank=True),
        'description': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_PRODUCT_PATCH = inline_serializer(
    name='ProductPatchMultipartRequest',
    fields={
        'title': serializers.CharField(required=False, allow_blank=True),
        'brandId': serializers.IntegerField(required=False),
        'categoryId': serializers.IntegerField(required=False),
        'conditionId': serializers.UUIDField(required=False, allow_null=True),
        'modelId': serializers.IntegerField(required=False, allow_null=True),
        'variants': serializers.CharField(required=False, allow_blank=True),
        'isNew': serializers.BooleanField(required=False),
        'isHit': serializers.BooleanField(required=False),
        'isBt': serializers.BooleanField(required=False),
        'article': serializers.CharField(required=False, allow_blank=True),
        'description': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_PRODUCT_VARIANT_PATCH = inline_serializer(
    name='ProductVariantPatchRequest',
    fields={
        'price': serializers.FloatField(required=False),
        'oldPrice': serializers.FloatField(required=False),
        'discount': serializers.IntegerField(required=False),
        'isAvailable': serializers.BooleanField(required=False),
        'colorId': serializers.IntegerField(required=False),
        'diagonal': serializers.CharField(required=False, allow_blank=True),
        'size': serializers.CharField(required=False, allow_blank=True),
        'images': serializers.JSONField(required=False),
        'simTypes': serializers.JSONField(required=False, help_text='Массив { simTypeId, price }'),
    },
)

REQ_CONSULTATION_FORM = inline_serializer(
    name='ConsultationRequest',
    fields={
        'name': serializers.CharField(help_text='Имя клиента'),
        'phone': serializers.CharField(help_text='Телефон'),
        'consent': serializers.BooleanField(required=False, help_text='Согласие на обработку данных'),
    },
)

REQ_HELP_FORM = inline_serializer(
    name='HelpFormRequest',
    fields={
        'name': serializers.CharField(),
        'phone': serializers.CharField(),
        'consent': serializers.BooleanField(required=False),
    },
)

REQ_TRADEIN_FORM = inline_serializer(
    name='TradeInFormRequest',
    fields={
        'name': serializers.CharField(),
        'phone': serializers.CharField(),
        'oldDevice': serializers.CharField(required=False, allow_blank=True),
        'productTitle': serializers.CharField(required=False, allow_blank=True),
        'productId': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_REPAIR_FORM = inline_serializer(
    name='RepairSiteFormRequest',
    fields={
        'name': serializers.CharField(),
        'phone': serializers.CharField(),
        'model': serializers.CharField(),
        'problem': serializers.CharField(),
        'previouslyServiced': serializers.CharField(
            required=False, allow_blank=True, help_text='yes или no'
        ),
        'agreeToPrivacy': serializers.BooleanField(required=False),
    },
)

REQ_ORDER_PRODUCT_LINE = inline_serializer(
    name='OrderCreateProductLine',
    fields={
        'product_id': serializers.CharField(help_text='UUID варианта (ProductVariant)'),
        'quantity': serializers.IntegerField(help_text='Количество, >= 1'),
    },
)

REQ_ORDER_CREATE = inline_serializer(
    name='OrderCreateRequest',
    fields={
        'fullName': serializers.CharField(help_text='ФИО покупателя'),
        'email': serializers.EmailField(help_text='Email покупателя'),
        'phone': serializers.CharField(help_text='Телефон покупателя'),
        'products_list': serializers.ListField(
            child=REQ_ORDER_PRODUCT_LINE,
            help_text='Список позиций заказа',
        ),
        'isDelivery': serializers.BooleanField(required=False, help_text='Доставка'),
        'isPickup': serializers.BooleanField(required=False, help_text='Самовывоз'),
        'apartment': serializers.CharField(required=False, allow_blank=True, help_text='Квартира'),
        'entrance': serializers.CharField(required=False, allow_blank=True, help_text='Подъезд'),
        'floor': serializers.CharField(required=False, allow_blank=True, help_text='Этаж'),
    },
)

RES_ORDER_LINE = inline_serializer(
    name='OrderProductLine',
    fields={
        'product_id': serializers.CharField(help_text='UUID варианта (ProductVariant)'),
        'productId': serializers.IntegerField(help_text='ID товара (Product)'),
        'title': serializers.CharField(),
        'slug': serializers.CharField(),
        'quantity': serializers.IntegerField(),
        'unitPrice': serializers.IntegerField(),
        'lineTotal': serializers.IntegerField(),
        'image': serializers.CharField(allow_null=True),
    },
)

RES_ORDER = inline_serializer(
    name='OrderResponse',
    fields={
        'id': serializers.CharField(),
        'fullName': serializers.CharField(),
        'email': serializers.EmailField(),
        'phone': serializers.CharField(),
        'totalPrice': serializers.IntegerField(),
        'isDelivery': serializers.BooleanField(),
        'isPickup': serializers.BooleanField(),
        'deliveryType': serializers.CharField(),
        'apartment': serializers.CharField(),
        'entrance': serializers.CharField(),
        'floor': serializers.CharField(),
        'products_list': serializers.ListField(child=RES_ORDER_LINE),
        'createdAt': serializers.CharField(),
        'updatedAt': serializers.CharField(),
    },
)

# --- Корзина ---
REQ_CART_ADD = inline_serializer(
    name='CartAddRequest',
    fields={
        'variantId': serializers.CharField(help_text='UUID варианта ProductVariant'),
        'quantity': serializers.IntegerField(required=False, default=1, help_text='По умолчанию 1'),
    },
)

REQ_CART_PATCH = inline_serializer(
    name='CartPatchRequest',
    fields={
        'quantity': serializers.IntegerField(help_text='Новое количество (>= 1)'),
    },
)

RES_CART_NAMED = inline_serializer(
    name='CartNamedEntity',
    fields={
        'id': serializers.IntegerField(required=False),
        'name': serializers.CharField(),
        'slug': serializers.CharField(required=False),
        'hex': serializers.CharField(required=False),
    },
)

RES_CART_PRODUCT = inline_serializer(
    name='CartProductCard',
    fields={
        'variantId': serializers.CharField(),
        'productId': serializers.IntegerField(),
        'title': serializers.CharField(),
        'slug': serializers.CharField(),
        'price': serializers.IntegerField(),
        'oldPrice': serializers.IntegerField(allow_null=True),
        'discount': serializers.IntegerField(allow_null=True),
        'isAvailable': serializers.BooleanField(),
        'image': serializers.CharField(allow_null=True, help_text='Полный URL изображения'),
        'memory': RES_CART_NAMED,
        'color': RES_CART_NAMED,
        'brand': RES_CART_NAMED,
        'category': RES_CART_NAMED,
    },
)

RES_CART_ITEM = inline_serializer(
    name='CartItemResponse',
    fields={
        'id': serializers.CharField(help_text='UUID позиции корзины'),
        'variantId': serializers.CharField(help_text='UUID варианта'),
        'quantity': serializers.IntegerField(),
        'lineTotal': serializers.IntegerField(help_text='price * quantity'),
        'product': RES_CART_PRODUCT,
    },
)

RES_CART = inline_serializer(
    name='CartResponse',
    fields={
        'items': serializers.ListField(child=RES_CART_ITEM),
        'totalPrice': serializers.IntegerField(help_text='Сумма всех lineTotal'),
        'count': serializers.IntegerField(help_text='Количество позиций (для badge)'),
    },
)

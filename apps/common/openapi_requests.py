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
    fields={'name': serializers.CharField()},
)

REQ_BRAND_PATCH = inline_serializer(
    name='BrandPatchRequest',
    fields={'name': serializers.CharField(required=False, allow_blank=True)},
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
        'categoryId': serializers.IntegerField(required=False),
        'slug': serializers.CharField(required=False, allow_blank=True),
        'brandId': serializers.IntegerField(required=False),
        'modelId': serializers.IntegerField(required=False),
        'minPrice': serializers.FloatField(required=False),
        'maxPrice': serializers.FloatField(required=False),
        'memoryIds': serializers.ListField(child=serializers.IntegerField(), required=False),
        'colorIds': serializers.ListField(child=serializers.IntegerField(), required=False),
        'conditionIds': serializers.ListField(child=serializers.CharField(), required=False),
        'simTypeIds': serializers.ListField(child=serializers.CharField(), required=False),
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

REQ_ORDER_USER = inline_serializer(
    name='OrderWithUserRequest',
    fields={
        'products': serializers.JSONField(help_text='Массив позиций заказа'),
        'totalPrice': serializers.IntegerField(),
        'fio': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.EmailField(required=False, allow_null=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'address': serializers.CharField(required=False, allow_blank=True),
        'deltype': serializers.CharField(required=False, allow_blank=True),
    },
)

REQ_ORDER_CART = inline_serializer(
    name='OrderCartRequest',
    fields={
        'products': serializers.JSONField(required=False),
        'totalPrice': serializers.IntegerField(required=False),
        'fio': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.EmailField(required=False, allow_null=True),
    },
)

REQ_ORDER_ONE = inline_serializer(
    name='OrderOneItemRequest',
    fields={
        'product': serializers.JSONField(help_text='Объект одной позиции корзины'),
        'totalPrice': serializers.IntegerField(),
    },
)

REQ_QUICK_ORDER = inline_serializer(
    name='QuickOrderRequest',
    fields={
        'product': serializers.JSONField(),
        'totalPrice': serializers.IntegerField(),
        'fio': serializers.CharField(required=False, allow_blank=True),
        'phone': serializers.CharField(required=False, allow_blank=True),
        'email': serializers.EmailField(),
        'memory': serializers.CharField(required=False, allow_blank=True),
        'color': serializers.CharField(required=False, allow_blank=True),
    },
)

import os
from datetime import timedelta
from pathlib import Path


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None
    
    
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-5j0qzsb@7iul#y3n$1ok2o)z45ml^^8ei8y8c2*!8_qvc#k3(o'

DEBUG = True

ALLOWED_HOSTS = ["*"]


LOCAL_APPS = [
    'apps.common',
    'apps.store_core',
    'apps.accounts',
    'apps.catalog',
    'apps.blog',
    'apps.repair',
    'apps.site_content',
    'apps.storefront',
]

INSTALLED_APPS = [
    'daphne',
    'channels',
    'jazzmin',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'corsheaders',
    'django_filters',
    *LOCAL_APPS,
]

JAZZMIN_SETTINGS = {
    "site_title": "Genius Store",
    "site_header": "Genius Store",
    "site_brand": "Genius Store",
    "welcome_sign": "Панель управления магазином",
    "copyright": "Genius Store",
    "search_model": [
        "store_core.StoreUser",
        "store_core.Product",
        "store_core.ProductVariant",
        "store_core.StoreOrder",
    ],
    "topmenu_links": [
        {"name": "API Docs", "url": "/docs/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": ["auth", "sites"],
    "hide_models": [
        "store_core.productvariantsimtype",
        "store_core.blogsteps",
        "store_core.servicemodel",
        "store_core.service",
        "store_core.storeadmin",
        "storefront.favorite",
        "storefront.cartitem",
        "store_core.orderitem",
    ],
    "order_with_respect_to": [
        "store_core",
        "store_core.storeuser",
        "store_core.category",
        "store_core.brand",
        "store_core.banner",
        "store_core.productmodel",
        "store_core.product",
        "store_core.productimage",
        "store_core.productvariant",
        "store_core.condition",
        "store_core.color",
        "store_core.memory",
        "store_core.blogcategory",
        "store_core.blog",
        "store_core.info",
        "store_core.simtype",
        "store_core.storeorder",
        "store_core.orderitem",
        "store_core.servicebrand",
        "storefront",
        "storefront.review",
        "storefront.sitesettings",
    ],
    "icons": {
        "store_core": "fas fa-store",
        "storefront": "fas fa-cog",
        "store_core.storeuser": "fas fa-users",
        "store_core.storeorder": "fas fa-shopping-cart",
        "store_core.category": "fas fa-list",
        "store_core.brand": "fas fa-tag",
        "store_core.banner": "fas fa-image",
        "store_core.productmodel": "fas fa-mobile-alt",
        "store_core.product": "fas fa-box",
        "store_core.productimage": "fas fa-images",
        "store_core.productvariant": "fas fa-ruble-sign",
        "store_core.condition": "fas fa-check-circle",
        "store_core.color": "fas fa-palette",
        "store_core.memory": "fas fa-hdd",
        "store_core.blogcategory": "fas fa-folder",
        "store_core.blog": "fas fa-newspaper",
        "store_core.info": "fas fa-star",
        "store_core.simtype": "fas fa-sim-card",
        "store_core.servicebrand": "fas fa-tools",
        "storefront.review": "fas fa-comment",
        "storefront.sitesettings": "fas fa-sliders-h",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/admin_drawer.js",
    "related_modal_active": True,
    "show_ui_builder": False,
}

X_FRAME_OPTIONS = 'SAMEORIGIN'

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    "dark_mode_theme": None,
    "default_theme_mode": "light",
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-white",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "actions_sticky_top": False,
}

LOCAL_MIDDLEWARE = [
    'config.middleware.middleware.JsonErrorResponseMiddleware',
    'config.middleware.middleware.Custom404Middleware',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'config.middleware.apikey_middleware.BackendApiKeyMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    *LOCAL_MIDDLEWARE,
]

ROOT_URLCONF = 'config.urls'

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'geniusstore'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '0576'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = "/media/"
MEDIA_ROOT = "/var/www/media/"
PUBLIC_MEDIA_BASE_URL = os.getenv('PUBLIC_MEDIA_BASE_URL', 'https://admin.geniusstorerf.ru').strip()


LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    "PAGE_SIZE": 100,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=7),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    # Production (HTTPS — Django admin login uchun majburiy)
    "https://admin.geniusstorerf.ru",
    "https://geniusstorerf.ru",
    "https://www.geniusstorerf.ru",
    *[o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()],
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "https://admin.geniusstorerf.ru",
    "https://geniusstorerf.ru",
    "https://www.geniusstorerf.ru",
    *[o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()],
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'

SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True

SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Jazzmin related-modal (+) opens admin add form in iframe; default DENY blocks it.
X_FRAME_OPTIONS = 'SAMEORIGIN'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

#AUTH_USER_MODEL = 'accounts.CustomUser'

SITE_ID = 1


EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').strip().lower() in ('1', 'true', 'yes', 'y')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '').strip()
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '').strip()

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', '').strip() or (
    'django.core.mail.backends.smtp.EmailBackend'
    if (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
    else 'django.core.mail.backends.console.EmailBackend'
)

DEFAULT_FROM_EMAIL = (
    os.getenv('DEFAULT_FROM_EMAIL', '').strip()
    or EMAIL_HOST_USER
    or 'no-reply@medicalai.local'
)

SPECTACULAR_SETTINGS = {
    'TITLE': 'Genius Store API',
    'DESCRIPTION': (
        'REST API интернет-магазина Genius Store на Django REST Framework. '
        'База данных: PostgreSQL. Пользователи: httpOnly cookie `access_token` / `refresh_token` '
        '(JWT HS256, секрет `JWT_REFRESH_SECRET`). Админ-панель API: `Authorization: Bearer <token>`. '
        'Документация: `/docs/`.'
    ),
    'VERSION': 'v1',
    'COMPONENT_SPLIT_REQUEST': True,
    'TAGS': [
        {'name': 'Система', 'description': 'Служебные эндпоинты (проверка доступности API и т.п.).'},
        {'name': 'Авторизация', 'description': 'Обновление JWT из cookie, вход администратора.'},
        {'name': 'Пользователи — Список', 'description': 'Публичный список пользователей.'},
        {'name': 'Пользователи — Регистрация', 'description': 'Создание нового аккаунта и выдача JWT cookie.'},
        {'name': 'Пользователи — Авторизация', 'description': 'Вход и выход пользователя по email и паролю.'},
        {'name': 'Пользователи — Профиль', 'description': 'Просмотр и обновление профиля, смена аватара.'},
        {'name': 'Пользователи — Пароль', 'description': 'Сброс пароля по email и смена по старому значению.'},
        {'name': 'Пользователи — Управление', 'description': 'Удаление пользователя (только admin JWT).'},
        {'name': 'Администратор', 'description': 'Создание записей администратора.'},
        {
            'name': 'Товары — Витрина',
            'description': 'Списки, поиск, категории, карточка товара по id и slug (чтение).',
        },
        {
            'name': 'Товары — Управление',
            'description': 'Создание, изменение и удаление товара (включая multipart).',
        },
        {'name': 'Товары — Варианты', 'description': 'Частичное обновление варианта, удаление варианта и изображений.'},
        {'name': 'Заказы', 'description': 'Оформление заказа без авторизации: POST /api/order (fullName, email, phone).'},
        {'name': 'Заявки', 'description': 'Формы с сайта: помощь, Trade-in, ремонт (уведомления в Telegram и на почту).'},
        {'name': 'Фильтры — Отбор', 'description': 'Фильтрация каталога по критериям (POST).'},
        {'name': 'Фильтры — Справочники', 'description': 'Данные для построения фильтров, бренды и модели, проверка slug товара.'},
        {'name': 'Фильтры — Подборки', 'description': 'Готовые подборки витрины (хиты, скидки, новинки и т.д.).'},
        {'name': 'Фильтры — SIM', 'description': 'Служебные операции и выборка по типу SIM.'},
        {'name': 'Справочники — Бренды', 'description': 'Бренды техники.'},
        {'name': 'Справочники — Категории', 'description': 'Категории каталога.'},
        {'name': 'Справочники — Цвета', 'description': 'Цвета для вариантов товара.'},
        {'name': 'Справочники — Состояние', 'description': 'Состояние товара (новый, б/у и т.д.).'},
        {'name': 'Справочники — Память', 'description': 'Объёмы памяти.'},
        {'name': 'Справочники — Модели', 'description': 'Модели устройств в каталоге товаров.'},
        {'name': 'Справочники — SIM', 'description': 'Типы SIM-карт.'},
        {'name': 'Блог — Категории', 'description': 'Категории статей блога.'},
        {'name': 'Блог — Шаги', 'description': 'Шаги внутри статьи.'},
        {'name': 'Блог — Статьи', 'description': 'Статьи блога: список, по категории, по slug.'},
        {'name': 'Ремонт — Бренды', 'description': 'Бренды для раздела сервиса и ремонта.'},
        {'name': 'Ремонт — Модели', 'description': 'Модели устройств в сервисе.'},
        {'name': 'Ремонт — Услуги', 'description': 'Услуги и цены (работа, работа с запчастями).'},
        {'name': 'Сайт — Баннеры', 'description': 'Баннеры главной страницы (desktop и mobile).'},
        {'name': 'Сайт — Страницы', 'description': 'Текстовые информационные страницы и блоки.'},
        {'name': 'Сайт — Настройки', 'description': 'Контакты, соцсети, преимущества главной, категории для футера.'},
        {'name': 'Избранное', 'description': 'Список избранных товаров авторизованного пользователя.'},
        {'name': 'Корзина', 'description': 'Корзина пользователя: позиции, количество, итоговая сумма.'},
        {'name': 'Отзывы', 'description': 'Текстовые и видео-отзывы (Avito, Яндекс, сайт).'},
    ],
    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [],
    'GENERIC_ADDITIONAL_PROPERTIES': None,
    'CAMPAIGN': None,
    'CONTACT': {
        'name': 'Поддержка API Genius Store',
        'email': 'support@genius-store.ru',
    },
    'LICENSE': {
        'name': 'Проприетарная лицензия',
    },
}

PASSWORD_RESET_CODE_TTL_MINUTES = int(os.getenv('PASSWORD_RESET_CODE_TTL_MINUTES', '15'))
PASSWORD_RESET_SESSION_TTL_MINUTES = int(os.getenv('PASSWORD_RESET_SESSION_TTL_MINUTES', '15'))

JWT_REFRESH_SECRET = os.getenv('JWT_REFRESH_SECRET', SECRET_KEY)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '').strip()
BACKEND_API_KEY = os.getenv('BACKEND_API_KEY', '').strip()
REQUIRE_BACKEND_API_KEY = os.getenv('REQUIRE_BACKEND_API_KEY', 'false').strip().lower() in ('1', 'true', 'yes')

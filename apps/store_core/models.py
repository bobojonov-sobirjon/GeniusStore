"""
ORM mapping for the existing PostgreSQL schema created by Prisma (NestJS).
Tables and column names match Prisma defaults (quoted mixed-case identifiers).
"""
from __future__ import annotations

import uuid

from django.db import models

from apps.common.file_storage import image_upload_to
from apps.store_core import spec_types


class PrismaModel(models.Model):
    class Meta:
        abstract = True
        managed = False


class StoreAdmin(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    username = models.TextField('Имя пользователя')
    password = models.TextField('Пароль')

    class Meta:
        db_table = 'Admin'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'
        ordering = ('username',)

    def __str__(self) -> str:
        return self.username


class StoreUser(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.TextField('Имя', db_column='firstName', null=True, blank=True)
    last_name = models.TextField('Фамилия', db_column='lastName', null=True, blank=True)
    middle_name = models.TextField('Отчество', db_column='middleName', null=True, blank=True)
    email = models.TextField('Электронная почта', null=True, blank=True, unique=True)
    phone = models.TextField('Телефон', null=True, blank=True, unique=True)
    avatar = models.ImageField('Аватар', upload_to=image_upload_to, max_length=512, null=True, blank=True)
    password = models.TextField('Пароль')
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'User'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        if self.email:
            return self.email
        if self.phone:
            return self.phone
        return str(self.id)[:8]


class BlogCategory(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'BlogCategory'
        verbose_name = 'Категория блога'
        verbose_name_plural = 'Категории блога'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Blog(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField('Заголовок')
    slug = models.TextField('Слаг')
    content = models.TextField('Содержимое')
    blog_category = models.ForeignKey(
        BlogCategory,
        verbose_name='Категория',
        db_column='blogCategoryId',
        on_delete=models.RESTRICT,
        related_name='blogs',
    )
    image = models.ImageField('Изображение', upload_to=image_upload_to, max_length=512, null=True, blank=True)
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Blog'
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Статьи блога'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title


class BlogSteps(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField('Заголовок')
    content = models.TextField('Содержимое')
    blog = models.ForeignKey(
        Blog,
        verbose_name='Статья',
        db_column='blogId',
        on_delete=models.RESTRICT,
        related_name='blogSteps',
    )
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'BlogSteps'
        verbose_name = 'Шаг статьи'
        verbose_name_plural = 'Шаги статей'
        ordering = ('blog', 'created_at')

    def __str__(self) -> str:
        return f'{self.blog_id}: {self.title}'


class Category(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    name = models.TextField('Название')
    icon = models.ImageField('Иконка', upload_to=image_upload_to, max_length=512, null=True, blank=True)
    slug = models.TextField('Слаг', null=True, blank=True, unique=True)
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)

    class Meta:
        db_table = 'Category'
        verbose_name = 'Категория каталога'
        verbose_name_plural = 'Категории каталога'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Brand(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    name = models.TextField('Название')
    image = models.ImageField(
        'Изображение',
        upload_to=image_upload_to,
        max_length=512,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)

    class Meta:
        db_table = 'Brand'
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class ProductModel(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    name = models.TextField('Название')
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)

    class Meta:
        db_table = 'ProductModel'
        verbose_name = 'Модель устройства'
        verbose_name_plural = 'Модели устройств'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Condition(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    created_at = models.DateTimeField('Создано', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Condition'
        verbose_name = 'Состояние товара'
        verbose_name_plural = 'Состояния товаров'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class SimType(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название', unique=True)

    class Meta:
        db_table = 'SimType'
        verbose_name = 'Тип SIM'
        verbose_name_plural = 'Типы SIM'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Color(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    name = models.TextField('Название')
    hex = models.TextField('HEX-код', null=True, blank=True)
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Color'
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Memory(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    name = models.TextField('Название')
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)

    class Meta:
        db_table = 'Memory'
        verbose_name = 'Объём памяти'
        verbose_name_plural = 'Объёмы памяти'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Product(PrismaModel):
    id = models.AutoField('Идентификатор', primary_key=True)
    title = models.TextField('Название')
    rating = models.FloatField('Рейтинг', null=True, blank=True)
    is_available = models.BooleanField('В наличии', db_column='isAvailable', default=True)
    is_new = models.BooleanField('Новинка', db_column='isNew', default=False)
    is_hit = models.BooleanField('Хит', db_column='isHit', default=False)
    is_bt = models.BooleanField('Bluetooth', db_column='isBt', default=False)
    article = models.TextField('Артикул', null=True, blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    slug = models.TextField('Слаг', unique=True)

    brand = models.ForeignKey(
        Brand,
        verbose_name='Бренд',
        db_column='brandId',
        on_delete=models.RESTRICT,
        related_name='products',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        db_column='categoryId',
        on_delete=models.RESTRICT,
        related_name='products',
    )
    condition = models.ForeignKey(
        Condition,
        verbose_name='Состояние',
        db_column='conditionId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    product_model = models.ForeignKey(
        ProductModel,
        verbose_name='Модель',
        db_column='modelId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )

    type = models.TextField('Тип', null=True, blank=True)
    product_class = models.TextField('Класс', db_column='class', null=True, blank=True)
    line = models.TextField('Линейка', null=True, blank=True)
    series = models.TextField('Серия', null=True, blank=True)
    system = models.TextField('Система', null=True, blank=True)
    version = models.TextField('Версия', null=True, blank=True)
    diagonal = models.TextField('Диагональ', null=True, blank=True)
    size = models.TextField('Размер', null=True, blank=True)
    screen_type = models.TextField('Тип экрана', db_column='screenType', null=True, blank=True)
    resolution = models.TextField('Разрешение', null=True, blank=True)
    refresh_rate = models.TextField('Частота обновления', db_column='refreshRate', null=True, blank=True)
    density = models.TextField('Плотность пикселей', null=True, blank=True)
    brightness = models.TextField('Яркость', null=True, blank=True)
    glass = models.TextField('Стекло', null=True, blank=True)
    aod = models.TextField('Always On Display', null=True, blank=True)

    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title


class ProductImage(models.Model):
    """Django-managed product gallery images (uploads under MEDIA_ROOT/uploads/)."""

    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        db_column='productId',
        on_delete=models.CASCADE,
        related_name='product_images',
    )
    image = models.ImageField(
        'Изображение',
        upload_to=image_upload_to,
        max_length=512,
        blank=True,
    )
    alt = models.TextField('Alt текст', blank=True, default='')
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    is_primary = models.BooleanField('Главное фото', default=False)
    color = models.ForeignKey(
        'Color',
        verbose_name='Цвет',
        db_column='colorId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_images',
        help_text='Привязка к цвету: на сайте фото меняются при выборе цвета.',
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        db_table = 'ProductImage'
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ('sort_order', '-created_at')
        managed = True

    def __str__(self) -> str:
        return f'{self.product}: {self.image.name if self.image else "—"}'

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        return super().delete(*args, **kwargs)


class ProductCharacteristic(models.Model):
    """One product spec row: block type + title + value(s)."""

    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        db_column='productId',
        on_delete=models.CASCADE,
        related_name='characteristics',
    )
    spec_type = models.CharField(
        'Тип',
        max_length=32,
        db_column='type',
        choices=spec_types.SPEC_TYPE_CHOICES,
    )
    title = models.TextField('Название')
    value = models.TextField(
        'Значение',
        blank=True,
        default='',
        help_text='Одно значение или несколько строк (каждая строка — пункт списка на сайте).',
    )
    sort_order = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        db_table = 'ProductCharacteristic'
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товара'
        ordering = ('spec_type', 'sort_order', 'title')
        managed = True

    def __str__(self) -> str:
        return f'{spec_types.spec_type_label(self.spec_type)}: {self.title}'


class ProductVariant(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        db_column='productId',
        on_delete=models.RESTRICT,
        related_name='variants',
    )
    memory = models.ForeignKey(
        Memory,
        verbose_name='Память',
        db_column='memoryId',
        on_delete=models.RESTRICT,
        related_name='variants',
    )
    price = models.FloatField('Цена')
    old_price = models.FloatField('Старая цена', db_column='oldPrice', null=True, blank=True)
    discount = models.IntegerField('Скидка, %', null=True, blank=True)
    is_available = models.BooleanField('В наличии', db_column='isAvailable', default=True)
    description = models.TextField('Описание', null=True, blank=True)
    color = models.ForeignKey(
        Color,
        verbose_name='Цвет',
        db_column='colorId',
        on_delete=models.RESTRICT,
        related_name='variants',
    )
    images = models.JSONField('Изображения (JSON)', null=True, blank=True)
    diagonal = models.TextField('Диагональ', null=True, blank=True)
    size = models.TextField('Размер', null=True, blank=True)
    sim_type = models.ForeignKey(
        SimType,
        verbose_name='Тип SIM (основной)',
        db_column='simTypeId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variants_single',
    )
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'ProductVariant'
        verbose_name = 'Цена варианта'
        verbose_name_plural = 'Управление ценами'
        ordering = ('product', 'price')

    def __str__(self) -> str:
        return f'{self.product_id}: {self.price}'


class ProductVariantSimType(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    product_variant = models.ForeignKey(
        ProductVariant,
        verbose_name='Вариант товара',
        db_column='productVariantId',
        on_delete=models.CASCADE,
        related_name='sim_type_links',
    )
    sim_type = models.ForeignKey(
        SimType,
        verbose_name='Тип SIM',
        db_column='simTypeId',
        on_delete=models.RESTRICT,
        related_name='variant_links',
    )
    price = models.FloatField('Цена за тип SIM', null=True, blank=True)

    class Meta:
        db_table = 'ProductVariantSimType'
        verbose_name = 'Цена SIM для варианта'
        verbose_name_plural = 'Цены SIM для вариантов'
        ordering = ('product_variant',)

    def __str__(self) -> str:
        return f'{self.product_variant_id} → {self.sim_type_id}'


class StoreOrder(PrismaModel):
    class DeliveryType(models.TextChoices):
        DELIVERY = 'delivery', 'Доставка'
        PICKUP = 'pickup', 'Самовывоз'

    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    products = models.JSONField('Товары (JSON, legacy)', null=True, blank=True, default=list)
    total_sum = models.IntegerField('Сумма', db_column='totalSum')
    delivery_type = models.CharField(
        'Способ получения',
        max_length=16,
        choices=DeliveryType.choices,
        db_column='deliveryType',
        default=DeliveryType.DELIVERY,
    )
    apartment = models.CharField('Квартира', max_length=64, blank=True, default='')
    entrance = models.CharField('Подъезд', max_length=64, blank=True, default='')
    floor = models.CharField('Этаж', max_length=64, blank=True, default='')
    full_name = models.CharField('ФИО', max_length=255, db_column='fullName', blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    phone = models.CharField('Телефон', max_length=32, blank=True, default='')
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)
    user = models.ForeignKey(
        StoreUser,
        verbose_name='Пользователь',
        db_column='userId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    class Meta:
        db_table = 'Order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'Заказ {str(self.id)[:8]}… — {self.total_sum}'

    @property
    def is_delivery(self) -> bool:
        return self.delivery_type == self.DeliveryType.DELIVERY

    @property
    def is_pickup(self) -> bool:
        return self.delivery_type == self.DeliveryType.PICKUP


class OrderItem(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        StoreOrder,
        verbose_name='Заказ',
        db_column='orderId',
        on_delete=models.CASCADE,
        related_name='items',
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        verbose_name='Вариант товара',
        db_column='productVariantId',
        on_delete=models.RESTRICT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    unit_price = models.IntegerField('Цена за единицу', db_column='unitPrice')
    line_total = models.IntegerField('Сумма строки', db_column='lineTotal')
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)

    class Meta:
        db_table = 'OrderItem'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return f'{self.product_variant_id} × {self.quantity}'


class ServiceBrand(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    slug = models.TextField('Слаг', unique=True)
    image = models.ImageField('Изображение', upload_to=image_upload_to, max_length=512)
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'ServiceBrand'
        verbose_name = 'Бренд сервиса (ремонт)'
        verbose_name_plural = 'Бренды сервиса'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class ServiceModel(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    slug = models.TextField('Слаг', unique=True)
    service_brand = models.ForeignKey(
        ServiceBrand,
        verbose_name='Бренд сервиса',
        db_column='serviceBrandId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='models',
    )
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'ServiceModel'
        verbose_name = 'Модель сервиса'
        verbose_name_plural = 'Модели сервиса'
        ordering = ('service_brand', 'name')

    def __str__(self) -> str:
        return self.name


class Service(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    slug = models.TextField('Слаг', unique=True)
    labor_only = models.IntegerField('Только работа', db_column='laborOnly')
    labor_with_part = models.IntegerField('Работа с запчастью', db_column='laborWithPart')
    service_model = models.ForeignKey(
        ServiceModel,
        verbose_name='Модель сервиса',
        db_column='serviceModelId',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
    )
    created_at = models.DateTimeField('Создана', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Service'
        verbose_name = 'Услуга ремонта'
        verbose_name_plural = 'Услуги ремонта'
        ordering = ('service_model', 'name')

    def __str__(self) -> str:
        return self.name


class Banner(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField('Заголовок')
    description = models.TextField('Описание')
    img_pc = models.ImageField('Изображение (ПК)', upload_to=image_upload_to, max_length=512, db_column='imgPc')
    img_mobile = models.ImageField(
        'Изображение (мобильный)',
        upload_to=image_upload_to,
        max_length=512,
        db_column='imgMobile',
    )
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Banner'
        verbose_name = 'Баннер'
        verbose_name_plural = 'Баннеры'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.title


class Info(PrismaModel):
    id = models.UUIDField('Идентификатор', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField('Название')
    description = models.TextField('Описание', null=True, blank=True)
    created_at = models.DateTimeField('Создан', db_column='createdAt', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', db_column='updatedAt', auto_now=True)

    class Meta:
        db_table = 'Info'
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name

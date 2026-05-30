from __future__ import annotations

import uuid

from django.db import models


class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField('Пользователь', db_index=True)
    variant_id = models.UUIDField('Вариант товара', db_index=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        db_table = 'store_favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'variant_id'], name='uniq_favorite_user_variant'),
        ]

    def __str__(self) -> str:
        return f'{self.user_id} → {self.variant_id}'


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField('Пользователь', db_index=True)
    variant_id = models.UUIDField('Вариант товара', db_index=True)
    quantity = models.PositiveIntegerField('Количество', default=1)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        db_table = 'store_cart_item'
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'variant_id'], name='uniq_cart_user_variant'),
        ]

    def __str__(self) -> str:
        return f'{self.user_id} × {self.variant_id} ({self.quantity})'


class Review(models.Model):
    SOURCE_AVITO = 'avito'
    SOURCE_YANDEX = 'yandex'
    SOURCE_SITE = 'site'
    SOURCE_CHOICES = [
        (SOURCE_AVITO, 'Avito'),
        (SOURCE_YANDEX, 'Yandex Maps'),
        (SOURCE_SITE, 'Сайт'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author_name = models.CharField('Автор', max_length=255)
    text = models.TextField('Текст', blank=True, default='')
    rating = models.PositiveSmallIntegerField('Оценка', default=5)
    source = models.CharField('Источник', max_length=32, choices=SOURCE_CHOICES, default=SOURCE_SITE)
    video_url = models.URLField('Видео URL', blank=True, default='')
    thumbnail = models.TextField('Превью', blank=True, default='')
    is_published = models.BooleanField('Опубликован', default=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        db_table = 'store_review'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.author_name} ({self.rating}★)'


class SiteSettings(models.Model):
    """Одна запись с pk=1 — контакты и блоки главной."""

    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    phone = models.CharField('Телефон', max_length=64, default='+7 (966) 861-52-42')
    email = models.EmailField('Email', default='info@geniusstore.ru')
    address = models.TextField(
        'Адрес',
        default='Санкт-Петербург, Невский проспект 112-114',
    )
    telegram_url = models.URLField('Telegram', blank=True, default='')
    vk_url = models.URLField('VK', blank=True, default='')
    whatsapp_url = models.URLField('WhatsApp', blank=True, default='')
    map_lat = models.FloatField('Широта', null=True, blank=True)
    map_lng = models.FloatField('Долгота', null=True, blank=True)
    advantages = models.JSONField('Преимущества (JSON)', default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_site_settings'
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self) -> str:
        return 'Настройки Genius Store'

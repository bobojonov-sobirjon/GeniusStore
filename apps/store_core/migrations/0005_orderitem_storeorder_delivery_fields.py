# Generated manually for order refactor

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0004_alter_info_options_alter_productvariant_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeorder',
            name='apartment',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Квартира'),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='delivery_type',
            field=models.CharField(
                choices=[('delivery', 'Доставка'), ('pickup', 'Самовывоз')],
                db_column='deliveryType',
                default='delivery',
                max_length=16,
                verbose_name='Способ получения',
            ),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='entrance',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Подъезд'),
        ),
        migrations.AddField(
            model_name='storeorder',
            name='floor',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Этаж'),
        ),
        migrations.AlterField(
            model_name='storeorder',
            name='products',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Товары (JSON, legacy)'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Количество')),
                ('unit_price', models.IntegerField(db_column='unitPrice', verbose_name='Цена за единицу')),
                ('line_total', models.IntegerField(db_column='lineTotal', verbose_name='Сумма строки')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='createdAt', verbose_name='Создан')),
                ('order', models.ForeignKey(db_column='orderId', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store_core.storeorder', verbose_name='Заказ')),
                ('product_variant', models.ForeignKey(db_column='productVariantId', on_delete=django.db.models.deletion.RESTRICT, related_name='order_items', to='store_core.productvariant', verbose_name='Вариант товара')),
            ],
            options={
                'verbose_name': 'Позиция заказа',
                'verbose_name_plural': 'Позиции заказа',
                'db_table': 'OrderItem',
                'ordering': ('created_at',),
            },
        ),
    ]

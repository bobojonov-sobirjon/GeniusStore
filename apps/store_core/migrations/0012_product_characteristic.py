# Generated manually — flat ProductCharacteristic replaces nested spec groups.

import uuid

import django.db.models.deletion
from django.db import migrations, models


SPEC_TYPE_CHOICES = [
    ('main', 'Основные характеристики'),
    ('processor', 'Процессор'),
    ('body', 'Корпус'),
    ('display', 'Дисплей'),
    ('camera', 'Камера'),
    ('front_camera', 'Фронтальная камера'),
    ('video', 'Запись видео'),
    ('power', 'Питание'),
    ('connectivity', 'Связь и подключение'),
    ('multimedia', 'Мультимедиа'),
    ('factory', 'Заводские данные'),
    ('battery_life', 'Время работы'),
    ('package', 'Комплектация'),
    ('extra', 'Дополнительно'),
]

LEGACY_GROUP_TITLE_TO_TYPE = {label: key for key, label in SPEC_TYPE_CHOICES}

VARIANT_SOURCE_CHOICES = [
    ('', 'Вручную'),
    ('memory', 'Память (вариант)'),
    ('color', 'Цвет (вариант)'),
    ('sim', 'SIM (вариант)'),
    ('series', 'Серия'),
    ('model', 'Модель'),
    ('condition', 'Состояние'),
    ('system', 'Операционная система'),
]


def _legacy_type(title: str) -> str:
    key = LEGACY_GROUP_TITLE_TO_TYPE.get((title or '').strip())
    return key if key else 'extra'


def migrate_specs_forward(apps, schema_editor):
    ProductSpecItem = apps.get_model('store_core', 'ProductSpecItem')
    ProductSpecGroup = apps.get_model('store_core', 'ProductSpecGroup')
    ProductCharacteristic = apps.get_model('store_core', 'ProductCharacteristic')

    for item in ProductSpecItem.objects.all().iterator():
        product_id = item.product_id
        group_title = (item.group_title or '').strip()
        if item.group_id:
            group = ProductSpecGroup.objects.filter(pk=item.group_id).first()
            if group:
                product_id = product_id or group.product_id
                if not group_title:
                    group_title = (group.title or '').strip()
        if not product_id:
            continue

        values = item.values if isinstance(item.values, list) else []
        value_text = '\n'.join(str(v).strip() for v in values if v is not None and str(v).strip())

        ProductCharacteristic.objects.create(
            id=item.id,
            product_id=product_id,
            spec_type=_legacy_type(group_title),
            title=item.label or '',
            value=value_text,
            variant_source=item.variant_source or '',
            sort_order=item.sort_order or 0,
        )


def migrate_specs_backward(apps, schema_editor):
    ProductCharacteristic = apps.get_model('store_core', 'ProductCharacteristic')
    ProductCharacteristic.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0011_productspecitem_product_inline'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCharacteristic',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('spec_type', models.CharField(choices=SPEC_TYPE_CHOICES, db_column='type', max_length=32, verbose_name='Тип')),
                ('title', models.TextField(verbose_name='Название')),
                ('value', models.TextField(blank=True, default='', help_text='Одно значение или несколько строк (каждая строка — пункт списка на сайте).', verbose_name='Значение')),
                ('variant_source', models.CharField(blank=True, choices=VARIANT_SOURCE_CHOICES, default='', help_text='Для Память/Цвет/SIM оставьте «Значение» пустым — подставится автоматически.', max_length=32, verbose_name='Источник из варианта')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('product', models.ForeignKey(db_column='productId', on_delete=django.db.models.deletion.CASCADE, related_name='characteristics', to='store_core.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Характеристика товара',
                'verbose_name_plural': 'Характеристики товара',
                'db_table': 'ProductCharacteristic',
                'ordering': ('spec_type', 'sort_order', 'title'),
                'managed': True,
            },
        ),
        migrations.RunPython(migrate_specs_forward, migrate_specs_backward),
        migrations.DeleteModel(
            name='ProductSpecItem',
        ),
        migrations.DeleteModel(
            name='ProductSpecGroup',
        ),
    ]

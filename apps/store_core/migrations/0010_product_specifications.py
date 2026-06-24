# Generated manually for product characteristic groups

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0009_productimage_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSpecGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('title', models.TextField(verbose_name='Группа характеристик')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок группы')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('product', models.ForeignKey(db_column='productId', on_delete=django.db.models.deletion.CASCADE, related_name='spec_groups', to='store_core.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Группа характеристик',
                'verbose_name_plural': 'Группы характеристик',
                'db_table': 'ProductSpecGroup',
                'ordering': ('sort_order', 'title'),
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProductSpecItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('label', models.TextField(verbose_name='Название')),
                ('values', models.JSONField(blank=True, default=list, help_text='Список строк. Несколько значений — маркированный список на сайте.', verbose_name='Значения')),
                ('variant_source', models.CharField(blank=True, choices=[('', 'Вручную'), ('memory', 'Память (вариант)'), ('color', 'Цвет (вариант)'), ('sim', 'SIM (вариант)'), ('series', 'Серия'), ('model', 'Модель'), ('condition', 'Состояние'), ('system', 'Операционная система')], default='', help_text='Если выбрано — значения подставляются из товара/варианта автоматически.', max_length=32, verbose_name='Источник из варианта')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('group', models.ForeignKey(db_column='groupId', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store_core.productspecgroup', verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Характеристика',
                'verbose_name_plural': 'Характеристики',
                'db_table': 'ProductSpecItem',
                'ordering': ('sort_order', 'label'),
                'managed': True,
            },
        ),
    ]

"""Expand ProductCharacteristic.spec_type choices for mobiles."""

from django.db import migrations, models


SPEC_TYPE_CHOICES = [
    ('main', 'Основные'),
    ('general', 'Общие'),
    ('processor', 'Процессор'),
    ('storage', 'Накопитель'),
    ('body', 'Корпус'),
    ('construction', 'Конструкция'),
    ('display', 'Дисплей'),
    ('camera', 'Камера'),
    ('front_camera', 'Фронтальная камера'),
    ('video', 'Запись видео'),
    ('power', 'Питание'),
    ('battery_life', 'Время работы'),
    ('connectivity', 'Связь'),
    ('connection', 'Подключение'),
    ('sound', 'Звук'),
    ('multimedia', 'Мультимедиа'),
    ('factory', 'Заводские данные'),
    ('features', 'Особенности'),
    ('package', 'Комплектация'),
    ('extra', 'Дополнительно'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('store_core', '0019_productvariant_memory_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcharacteristic',
            name='spec_type',
            field=models.CharField(
                choices=SPEC_TYPE_CHOICES,
                db_column='type',
                max_length=32,
                verbose_name='Тип',
            ),
        ),
    ]

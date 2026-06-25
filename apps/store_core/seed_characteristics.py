"""Demo characteristic rows for seed command."""
from __future__ import annotations

from apps.store_core.models import Product, ProductCharacteristic


def _add_rows(product: Product, spec_type: str, rows: list) -> None:
    for item_sort, row in enumerate(rows):
        if len(row) != 2:
            continue
        title, value = row
        if isinstance(value, list):
            value_text = '\n'.join(str(v) for v in value)
        else:
            value_text = str(value) if value else ''
        ProductCharacteristic.objects.update_or_create(
            product=product,
            spec_type=spec_type,
            title=title,
            defaults={
                'sort_order': item_sort,
                'value': value_text,
            },
        )


def seed_iphone_13_characteristics(product: Product) -> None:
    """Whale Store style grouped specs for demo product apple-iphone-13."""
    _add_rows(product, 'main', [
        ('Серия', 'iPhone 13'),
        ('Память', '128 GB'),
        ('Цвет', 'Green'),
        ('SIM-карта', 'nano-SIM + eSIM'),
        ('Операционная система', 'iOS'),
    ])
    _add_rows(product, 'processor', [
        ('Процессор', 'Apple A15 Bionic'),
    ])
    _add_rows(product, 'body', [
        ('Материал', 'алюминий'),
        ('Высота, мм', '146.7'),
        ('Ширина, мм', '71.5'),
        ('Толщина, мм', '7.65'),
        ('Вес, г', '173'),
    ])
    _add_rows(product, 'display', [
        ('Диагональ', '6.1"'),
        ('Разрешение', '2532×1170'),
        ('Тип дисплея', 'Super Retina XDR OLED'),
        ('Плотность пикселей на дюйм', '460 пикс/дюйм'),
        ('Яркость', '1200 нит'),
        ('Частота обновления экрана', '60 Гц'),
        ('Стекло', 'Ceramic Shield'),
        ('Always On Display', 'Нет'),
    ])
    _add_rows(product, 'camera', [
        ('Разрешение камеры', '12 Мп + 12 Мп'),
        ('Диафрагма', 'основная: f/1.6, сверхширокоугольная: f/2.4'),
        ('Зум (фото)', ['цифровой 5x', 'оптический 2x']),
        ('Защита объектива', 'сапфировое стекло'),
        ('Функции камеры', [
            'ночной режим',
            'Smart HDR 4',
            'панорамная съёмка',
            'серийная съёмка',
            'портретный режим',
        ]),
    ])
    _add_rows(product, 'front_camera', [
        ('Разрешение фронтальной камеры', '12 Мп'),
        ('Диафрагма фронтальной камеры', 'f/2.2'),
        ('Разрешение видео фронтальной камеры', [
            'HD-видео 1080p с частотой 25, 30 или 60 кадров/с',
        ]),
        ('Функции фронтальной камеры', [
            'Smart HDR 4',
            'кинематографическая стабилизация видео',
            'Retina Flash с True Tone',
            'серийная съёмка',
        ]),
    ])
    _add_rows(product, 'video', [
        ('Разрешение видео', [
            'HD-видео 1080p с частотой 25, 30 или 60 кадров/с',
            '4K с частотой 24, 25, 30 или 60 кадров/с',
        ]),
        ('Разрешение замедленного видео', [
            'HD-видео 1080p с частотой 120 и 240 кадров/с',
        ]),
        ('Функции видео', [
            'стабилизация видео',
            'фокусировка касанием',
            'распознавание лиц',
            'форматы записанного видео: HEVC и H.264',
        ]),
    ])
    _add_rows(product, 'power', [
        ('Тип аккумулятора', 'Li-Ion'),
        ('Воспроизведение видео', 'до 19 часов'),
    ])
    _add_rows(product, 'connectivity', [
        ('Сотовая и беспроводная связь', [
            '5G (sub-6 GHz)',
            'Gigabit Class LTE',
            'Wi-Fi 6 (802.11ax)',
            'Bluetooth 5.0',
            'NFC',
        ]),
        ('Навигация', ['GPS', 'ГЛОНАСС', 'Galileo', 'QZSS', 'BeiDou']),
        ('Разъёмы', 'Lightning'),
    ])
    _add_rows(product, 'factory', [
        ('Страна производителя', 'Китай'),
        ('Гарантия, мес', '12'),
    ])
    _add_rows(product, 'extra', [
        ('Тип разблокировки', 'Face ID'),
        ('Датчики', [
            'акселерометр',
            'гироскоп',
            'барометр',
            'датчик освещённости',
            'датчик приближения',
        ]),
        ('В комплекте', [
            'кабель USB-C — Lightning (1 м)',
            'руководство пользователя',
        ]),
    ])


def seed_product_characteristics(products: list[Product]) -> None:
    for product in products:
        if product.slug == 'apple-iphone-13':
            seed_iphone_13_characteristics(product)
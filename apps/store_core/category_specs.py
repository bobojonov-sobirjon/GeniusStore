"""Which Product fields appear in admin and in API specs per category slug."""
from __future__ import annotations

from typing import Any

# Slug aliases (production / seed may use different slugs).
_SLUG_ALIASES = {
    'smartphones': 'smartfony',
    'smartphone': 'smartfony',
    'telefony': 'smartfony',
    'phones': 'smartfony',
    'vacuum': 'pylesosy',
    'vacuums': 'pylesosy',
    'headphones': 'naushniki',
    'consoles': 'igrovye-konsoli',
    'accessories': 'aksessuary',
}

# Product model field names (not variant fields).
CATEGORY_SPEC_FIELDS: dict[str, tuple[str, ...]] = {
    'smartfony': (
        'product_model', 'condition', 'diagonal', 'screen_type', 'resolution',
        'refresh_rate', 'density', 'brightness', 'glass', 'aod',
    ),
    'pylesosy': (
        'product_model', 'condition', 'type', 'system', 'version', 'line',
    ),
    'naushniki': (
        'product_model', 'condition', 'type', 'line', 'series', 'version',
    ),
    'igrovye-konsoli': (
        'product_model', 'condition', 'type', 'system', 'version', 'line',
    ),
    'aksessuary': (
        'product_model', 'condition', 'type', 'size', 'line', 'series',
    ),
    'default': (
        'product_model', 'condition', 'type', 'diagonal', 'size', 'line', 'series',
    ),
}

FIELD_LABELS: dict[str, str] = {
    'product_model': 'Модель',
    'condition': 'Состояние',
    'type': 'Тип',
    'product_class': 'Класс',
    'line': 'Линейка',
    'series': 'Серия',
    'system': 'Система',
    'version': 'Версия',
    'diagonal': 'Диагональ / экран',
    'size': 'Размер',
    'screen_type': 'Тип экрана',
    'resolution': 'Разрешение',
    'refresh_rate': 'Частота обновления',
    'density': 'Плотность пикселей',
    'brightness': 'Яркость',
    'glass': 'Стекло',
    'aod': 'Always On Display',
    'memory': 'Память',
    'color': 'Цвет',
}


def normalize_category_slug(slug: str | None) -> str:
    if not slug:
        return 'default'
    key = slug.strip().lower()
    return _SLUG_ALIASES.get(key, key)


def spec_field_names_for_category(slug: str | None) -> tuple[str, ...]:
    key = normalize_category_slug(slug)
    return CATEGORY_SPEC_FIELDS.get(key, CATEGORY_SPEC_FIELDS['default'])


def _product_field_value(product: Any, field_name: str) -> str | None:
    if field_name == 'product_model':
        pm = getattr(product, 'product_model', None)
        return pm.name if pm else None
    if field_name == 'condition':
        c = getattr(product, 'condition', None)
        return c.name if c else None
    value = getattr(product, field_name, None)
    if value is None or value == '':
        return None
    return str(value)


def build_specifications(product: Any, variant: Any | None = None) -> list[dict[str, Any]]:
    """Short specs for product card (Краткие характеристики)."""
    category = getattr(product, 'category', None)
    slug = category.slug if category else None
    fields = spec_field_names_for_category(slug)

    rows: list[dict[str, Any]] = []

    if variant is not None:
        memory = getattr(variant, 'memory', None)
        color = getattr(variant, 'color', None)
        if memory:
            rows.append({
                'key': 'memory',
                'label': FIELD_LABELS['memory'],
                'value': memory.name,
            })
        if color:
            rows.append({
                'key': 'color',
                'label': FIELD_LABELS['color'],
                'value': color.name,
            })

    for name in fields:
        if name in ('memory', 'color'):
            continue
        value = _product_field_value(product, name)
        rows.append({
            'key': name,
            'label': FIELD_LABELS.get(name, name),
            'value': value,
        })

    return rows

"""Product characteristic block types (group headings on the storefront)."""
from __future__ import annotations

SPEC_TYPE_CHOICES: tuple[tuple[str, str], ...] = (
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
)

SPEC_TYPE_LABELS = dict(SPEC_TYPE_CHOICES)

SPEC_TYPE_ORDER = {key: idx for idx, (key, _) in enumerate(SPEC_TYPE_CHOICES)}

# Migrate legacy group titles from ProductSpecGroup.
LEGACY_GROUP_TITLE_TO_TYPE: dict[str, str] = {
    label: key for key, label in SPEC_TYPE_CHOICES
}


def spec_type_label(spec_type: str) -> str:
    return SPEC_TYPE_LABELS.get(spec_type, spec_type)

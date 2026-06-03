"""Build absolute media URLs for API responses."""
from __future__ import annotations

from typing import Any

from django.conf import settings


def _normalize_media_path(path: str) -> str:
    path = path.strip()
    if path.startswith(('http://', 'https://')):
        return path
    if path.startswith('/media/'):
        return path
    if path.startswith('/uploads/'):
        return f'/media{path}'
    if path.startswith('uploads/'):
        return f'/media/{path}'
    return f'/media/uploads/{path.lstrip("/")}'


def media_url(path: str | None, request=None) -> str | None:
    if not path:
        return None
    if path.startswith(('http://', 'https://')):
        return path

    normalized = _normalize_media_path(path)
    base = (getattr(settings, 'PUBLIC_MEDIA_BASE_URL', '') or '').strip().rstrip('/')
    if not base and request is not None:
        base = request.build_absolute_uri('/').rstrip('/')
    if base:
        return f'{base}{normalized}'
    return normalized


def media_url_images(images: Any, request=None) -> list[Any]:
    """Normalize product variant image list: full URLs in url/path/src fields."""
    if not images or not isinstance(images, list):
        return []
    out: list[Any] = []
    for img in images:
        if isinstance(img, str):
            out.append(media_url(img, request))
            continue
        if isinstance(img, dict):
            item = dict(img)
            for key in ('url', 'path', 'src'):
                if item.get(key):
                    item[key] = media_url(str(item[key]), request)
            out.append(item)
            continue
        out.append(img)
    return out


def media_url_fields(data: dict[str, Any], fields: tuple[str, ...], request=None) -> dict[str, Any]:
    out = dict(data)
    for field in fields:
        if field in out and out[field]:
            out[field] = media_url(str(out[field]), request)
    return out


def serialize_values_row(row: dict | None, request=None, media_fields: tuple[str, ...] = ()) -> dict | None:
    if not row:
        return None
    out: dict[str, Any] = {}
    for key, value in row.items():
        if value is None:
            out[key] = None
        elif hasattr(value, 'hex') and hasattr(value, 'int'):  # UUID
            out[key] = str(value)
        elif hasattr(value, 'isoformat'):
            out[key] = value.isoformat()
        else:
            out[key] = value
    if media_fields:
        out = media_url_fields(out, media_fields, request)
    return out


def serialize_values_list(rows: list[dict], request=None, media_fields: tuple[str, ...] = ()) -> list[dict]:
    return [serialize_values_row(row, request, media_fields) or {} for row in rows]

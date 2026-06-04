"""Save uploaded files under MEDIA_ROOT / uploads / <type> (Nest parity)."""
from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings

IMAGE_UPLOAD_TO = 'uploads/image/'


def image_upload_to(instance, filename: str) -> str:
    ext = Path(filename).suffix.lstrip('.') or 'bin'
    return f'{IMAGE_UPLOAD_TO}{uuid.uuid4()}.{ext}'


def normalize_stored_image_path(path: str | None) -> str | None:
    """Normalize legacy DB paths to ImageField-relative paths under MEDIA_ROOT."""
    if not path:
        return path
    normalized = path.strip().lstrip('/')
    if normalized.startswith('uploads/'):
        return normalized
    if normalized.startswith('image/'):
        return f'uploads/{normalized}'
    return f'{IMAGE_UPLOAD_TO}{normalized.lstrip("/")}'


def save_upload_file(subdir: str, uploaded) -> str:
    """
    Returns relative path like 'image/<uuid>.ext' for DB storage.
    `uploaded` is a Django UploadedFile with .name and .chunks().
    """
    ext = Path(uploaded.name).suffix.lstrip('.') or 'bin'
    name = f'{uuid.uuid4()}.{ext}'
    base = Path(settings.MEDIA_ROOT) / 'uploads' / subdir
    base.mkdir(parents=True, exist_ok=True)
    dest = base / name
    with dest.open('wb') as f:
        for chunk in uploaded.chunks():
            f.write(chunk)
    return f'{subdir}/{name}'


def delete_media_relative(relative_path: str) -> None:
    if not relative_path:
        return
    if relative_path.startswith('uploads/'):
        p = Path(settings.MEDIA_ROOT) / relative_path
    else:
        p = Path(settings.MEDIA_ROOT) / 'uploads' / relative_path
    if p.is_file():
        p.unlink()

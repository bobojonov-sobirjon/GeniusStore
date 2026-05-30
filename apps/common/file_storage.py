"""Save uploaded files under MEDIA_ROOT / uploads / <type> (Nest parity)."""
from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings


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
    p = Path(settings.MEDIA_ROOT) / 'uploads' / relative_path
    if p.is_file():
        p.unlink()

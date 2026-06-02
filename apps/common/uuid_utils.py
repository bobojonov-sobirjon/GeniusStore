"""UUID helpers for API path parameters."""
from __future__ import annotations

import uuid


def normalize_uuid(value: str | None) -> str | None:
    """Return canonical UUID string or None if value is not a valid UUID."""
    if value is None:
        return None
    try:
        return str(uuid.UUID(str(value).strip()))
    except (ValueError, AttributeError, TypeError):
        return None

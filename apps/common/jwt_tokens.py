"""JWT helpers compatible with NestJS (@nestjs/jwt, HS256, same secret)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from django.conf import settings


def _secret() -> str:
    s = getattr(settings, 'JWT_REFRESH_SECRET', None) or settings.SECRET_KEY
    return str(s)


def encode_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    body = {**payload, 'exp': datetime.now(timezone.utc) + expires_delta, 'iat': datetime.now(timezone.utc)}
    return jwt.encode(body, _secret(), algorithm='HS256')


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, _secret(), algorithms=['HS256'])


def user_access_token(user_id: str, username: str | None) -> str:
    return encode_token({'sub': str(user_id), 'username': username or ''}, timedelta(minutes=15))


def user_refresh_token(user_id: str, username: str | None) -> str:
    return encode_token({'sub': str(user_id), 'username': username or ''}, timedelta(days=7))


def admin_token(admin_id: str, username: str) -> str:
    return encode_token({'sub': str(admin_id), 'username': username}, timedelta(days=7))

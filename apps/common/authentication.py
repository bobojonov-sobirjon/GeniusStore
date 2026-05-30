from __future__ import annotations

from dataclasses import dataclass

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.common import jwt_tokens
from apps.store_core.models import StoreAdmin, StoreUser


@dataclass
class StoreUserPrincipal:
    """Non-Django-auth user principal (cookie JWT, same as Nest UserGuard)."""

    pk: str
    email: str | None
    is_authenticated: bool = True
    is_anonymous: bool = False


@dataclass
class StoreAdminPrincipal:
    pk: str
    username: str
    is_authenticated: bool = True
    is_anonymous: bool = False


class CookieJWTAuthentication(BaseAuthentication):
    """Reads `access_token` httpOnly cookie (Nest parity)."""

    def authenticate(self, request):
        raw = request.COOKIES.get('access_token')
        if not raw:
            return None
        try:
            payload = jwt_tokens.decode_token(raw)
        except Exception as exc:
            raise AuthenticationFailed('Token expired or invalid') from exc
        uid = payload.get('sub')
        if not uid:
            raise AuthenticationFailed('Invalid token payload')
        user = StoreUser.objects.filter(pk=uid).first()
        if not user:
            raise AuthenticationFailed('User not found')
        return StoreUserPrincipal(pk=str(user.pk), email=user.email), None


class AdminBearerAuthentication(BaseAuthentication):
    """Authorization: Bearer <jwt> validated like Nest AdminGuard."""

    def authenticate(self, request):
        header = request.headers.get('Authorization') or ''
        if not header.startswith('Bearer '):
            return None
        token = header[7:].strip()
        if not token:
            return None
        try:
            payload = jwt_tokens.decode_token(token)
        except Exception:
            return None
        username = payload.get('username')
        if not username:
            return None
        admin = StoreAdmin.objects.filter(username=username).first()
        if not admin:
            return None
        return StoreAdminPrincipal(pk=str(admin.pk), username=admin.username), None

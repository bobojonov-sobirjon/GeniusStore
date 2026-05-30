from __future__ import annotations

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class AdminBearerAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.common.authentication.AdminBearerAuthentication"
    name = "AdminBearerAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT токен администратора. Получить через POST /api/auth/login-admin.",
        }


class UserCookieAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "apps.common.authentication.CookieJWTAuthentication"
    name = "UserCookieAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "Cookie пользователя `access_token` (выдаётся после /api/users/login или /api/users).",
        }


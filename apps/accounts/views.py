from __future__ import annotations

from asgiref.sync import sync_to_async
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common import jwt_tokens
from apps.common.authentication import (
    AdminBearerAuthentication,
    CookieJWTAuthentication,
    StoreAdminPrincipal,
    StoreUserPrincipal,
)
from apps.common.file_storage import save_upload_file
from apps.accounts import services_sync as acc
from apps.common.openapi_requests import (
    REQ_ADMIN_CREATE,
    REQ_ADMIN_LOGIN,
    REQ_USER_AVATAR,
    REQ_USER_LOGIN,
    REQ_USER_PROFILE_PATCH_JSON,
    REQ_USER_PROFILE_PATCH_MULTIPART,
    REQ_USER_REGISTER_JSON,
    REQ_USER_REGISTER_MULTIPART,
    REQ_USER_RESET_PASSWORD,
)


def _set_user_cookies(resp: Response, user) -> None:
    access = jwt_tokens.user_access_token(str(user.id), user.email)
    refresh = jwt_tokens.user_refresh_token(str(user.id), user.email)
    sec = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    resp.set_cookie(
        'access_token', access, httponly=True, secure=sec, samesite='Lax', max_age=15 * 60, path='/'
    )
    resp.set_cookie(
        'refresh_token', refresh, httponly=True, secure=sec, samesite='Lax', max_age=7 * 24 * 3600, path='/'
    )


def _clear_user_cookies(resp: Response) -> None:
    sec = getattr(settings, 'SESSION_COOKIE_SECURE', False)
    for name in ('access_token', 'refresh_token'):
        resp.delete_cookie(name, path='/', samesite='Lax', secure=sec)


@extend_schema(tags=['Авторизация'])
class AuthRefreshView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Обновление пары JWT по refresh cookie',
        description=(
            'Читает httpOnly cookie `refresh_token`, проверяет подпись (HS256, секрет `JWT_REFRESH_SECRET`). '
            'При успехе выдаёт новые `access_token` и `refresh_token` в cookie и возвращает профиль пользователя без пароля. '
            'Поведение соответствует NestJS `POST /api/auth/refresh`.'
        ),
        request=None,
        responses={200: OpenApiResponse(description='Объект пользователя (без поля password)')},
    )
    async def post(self, request):
        raw = (request.COOKIES.get('refresh_token') or '').strip()
        if not raw:
            raise PermissionDenied('No refresh token')
        try:
            payload = jwt_tokens.decode_token(raw)
        except Exception as exc:
            raise PermissionDenied('Invalid refresh token') from exc
        uid = payload.get('sub')
        user = await sync_to_async(acc.get_user)(str(uid))
        if not user:
            raise PermissionDenied('Invalid refresh token')
        resp = Response(acc.user_to_response(user))
        _set_user_cookies(resp, user)
        return resp


@extend_schema(tags=['Авторизация'])
class AuthAdminLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Вход администратора в панель',
        description=(
            'Пароль на сервере сравнивается с хэшем Argon2 (как в Nest, с суффиксом при создании админа). '
            'При успехе возвращается `{ "access_token": "<JWT>" }` для заголовка `Authorization: Bearer ...`. '
            'При неверных данных ответ `null` и статус 200 (как в исходном Nest).'
        ),
        request=REQ_ADMIN_LOGIN,
        responses={
            200: OpenApiResponse(
                description='Успех: `{ "access_token": "..." }`; неверные данные: `null` (тоже HTTP 200).'
            )
        },
    )
    async def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = (request.data.get('password') or '').strip()
        admin = await sync_to_async(acc.get_admin_by_username)(username)
        if not admin or not acc.verify_admin_password(admin.password, password):
            return Response(None, status=status.HTTP_200_OK)
        token = jwt_tokens.admin_token(str(admin.id), admin.username)
        return Response({'access_token': token})


@extend_schema(tags=['Пользователи — Список'])
class UserRootView(APIView):
    """GET/POST/PATCH на `/api/users` — как в Nest `UsersController`."""

    authentication_classes = [CookieJWTAuthentication]

    def get_permissions(self):
        if getattr(self, 'request', None) and self.request.method == 'PATCH':
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        tags=['Пользователи — Список'],
        summary='Список пользователей (публичный)',
        description=(
            'Возвращает массив пользователей с полями id, email, имя, телефон, аватар, даты без пароля. '
            'В Nest на этом маршруте не было обязательного AdminGuard — доступ открыт.'
        ),
    )
    async def get(self, request):
        data = await sync_to_async(acc.list_users_safe)()
        return Response(data)

    @extend_schema(
        tags=['Пользователи — Регистрация'],
        summary='Регистрация нового пользователя',
        description=(
            'Обязательные поля: `email`, `password`. Опционально: `firstName`, `lastName`, `middleName`, `phone`. '
            'Аватар — только в варианте `multipart/form-data` (поле `avatar`). После создания выставляются httpOnly cookie '
            '`access_token` (15 мин) и `refresh_token` (7 дней). Пароль хранится в виде Argon2-хэша.'
        ),
        request={
            'application/json': REQ_USER_REGISTER_JSON,
            'multipart/form-data': REQ_USER_REGISTER_MULTIPART,
        },
    )
    async def post(self, request):
        data = request.data
        if not data.get('email') or not data.get('password'):
            raise ValidationError('email и password обязательны')
        avatar = request.FILES.get('avatar')
        avatar_path = None
        if avatar:
            avatar_path = await sync_to_async(save_upload_file)('image', avatar)
        try:
            user = await sync_to_async(acc.create_user)(dict(data), avatar_path)
        except ValueError as e:
            raise ValidationError(str(e)) from e
        resp = Response(acc.user_to_response(user))
        _set_user_cookies(resp, user)
        return resp

    @extend_schema(
        tags=['Пользователи — Профиль'],
        summary='Обновление профиля текущего пользователя',
        description=(
            'Требуется валидный `access_token` в cookie (после входа или регистрации). '
            'Новый файл `avatar` — только в `multipart/form-data`. При указании `password` он будет перехэширован.'
        ),
        request={
            'application/json': REQ_USER_PROFILE_PATCH_JSON,
            'multipart/form-data': REQ_USER_PROFILE_PATCH_MULTIPART,
        },
    )
    async def patch(self, request):
        if not isinstance(request.user, StoreUserPrincipal):
            raise PermissionDenied('Пользователь не авторизован')
        avatar = request.FILES.get('avatar')
        avatar_path = None
        if avatar:
            avatar_path = await sync_to_async(save_upload_file)('image', avatar)
        body = dict(request.data)
        user = await sync_to_async(acc.update_user)(request.user.pk, body, avatar_path)
        return Response(acc.user_to_response(user))


@extend_schema(tags=['Пользователи — Авторизация'])
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Вход пользователя по email и паролю',
        description=(
            'При успехе в ответе — данные пользователя (без пароля) и cookie с JWT, как при регистрации.'
        ),
        request=REQ_USER_LOGIN,
    )
    async def post(self, request):
        email = (request.data.get('email') or '').strip()
        password = request.data.get('password') or ''
        try:
            user = await sync_to_async(acc.login_user)(email, password)
        except LookupError:
            raise NotFound('Пользователь не найден')
        except ValueError as e:
            raise ValidationError(str(e)) from e
        resp = Response(acc.user_to_response(user))
        _set_user_cookies(resp, user)
        return resp


@extend_schema(tags=['Пользователи — Авторизация'])
class UserLogoutView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Выход из аккаунта',
        description='Сбрасывает cookie `access_token` и `refresh_token` у клиента. Тело запроса не требуется.',
        request=None,
    )
    async def post(self, request):
        resp = Response({'message': 'Вы вышли из системы'})
        _clear_user_cookies(resp)
        return resp


@extend_schema(tags=['Пользователи — Пароль'])
class UserResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Сброс пароля по email',
        description=(
            'Укажите `emailOrUsername` или `email` — поиск пользователя по email. Генерируется новый пароль, '
            'сохраняется в БД и отправляется письмо (через настройки SMTP в Django). Ответ 204 при успехе.'
        ),
        request=REQ_USER_RESET_PASSWORD,
    )
    async def post(self, request):
        key = request.data.get('emailOrUsername') or request.data.get('email')
        if not key:
            raise ValidationError('emailOrUsername обязателен')
        try:
            await sync_to_async(acc.reset_password)(str(key).strip())
        except LookupError:
            raise NotFound('Пользователь не найден')
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Пользователи — Профиль'])
class UserChangeAvatarView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Смена аватара',
        description='Требуется cookie `access_token`. Форма: одно поле файла `avatar`. Возвращает обновлённого пользователя.',
        request={'multipart/form-data': REQ_USER_AVATAR},
    )
    async def post(self, request):
        if not isinstance(request.user, StoreUserPrincipal):
            raise PermissionDenied()
        avatar = request.FILES.get('avatar')
        if not avatar:
            raise ValidationError('Файл не найден')
        path = await sync_to_async(save_upload_file)('image', avatar)
        user = await sync_to_async(acc.change_avatar)(request.user.pk, path)
        return Response(acc.user_to_response(user))


class UserDetailView(APIView):
    authentication_classes = [AdminBearerAuthentication, CookieJWTAuthentication]

    def get_permissions(self):
        if getattr(self, 'request', None) and self.request.method == 'DELETE':
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        tags=['Пользователи — Профиль'],
        summary='Получить пользователя по UUID',
        description='Публичный GET: полный профиль без пароля. Идентификатор — строка UUID из таблицы `User`.',
    )
    async def get(self, request, pk: str):
        user = await sync_to_async(acc.get_user)(pk)
        if not user:
            raise NotFound('Bunday foydalanuvchi topilmadi')
        return Response(acc.user_to_response(user))

    @extend_schema(
        tags=['Пользователи — Управление'],
        summary='Удалить пользователя (только админ)',
        description='Требуется заголовок `Authorization: Bearer <admin JWT>`. Обычный пользовательский cookie не подходит.',
    )
    async def delete(self, request, pk: str):
        if not isinstance(request.user, StoreAdminPrincipal):
            raise PermissionDenied()
        await sync_to_async(acc.delete_user)(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Пользователи — Пароль'])
class UserChangePasswordView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Смена пароля по старому значению',
        description=(
            'Маршрут `PATCH /api/users/pass/{old}/{new}` — старый и новый пароль в URL (как в Nest). '
            'Требуется cookie `access_token`. Ответ 204 при успехе. Тело запроса не используется.'
        ),
        request=None,
        parameters=[
            OpenApiParameter(
                'old',
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                required=True,
                description='Текущий пароль (кодируйте спецсимволы в URL при необходимости)',
            ),
            OpenApiParameter(
                'new',
                OpenApiTypes.STR,
                OpenApiParameter.PATH,
                required=True,
                description='Новый пароль',
            ),
        ],
    )
    async def patch(self, request, old: str, new: str):
        if not isinstance(request.user, StoreUserPrincipal):
            raise PermissionDenied()
        try:
            await sync_to_async(acc.change_password)(request.user.pk, old, new)
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Администратор'])
class AdminCreateView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Создать учётную запись администратора',
        description=(
            'Пароль хэшируется с серверным суффиксом (совместимость с Nest). '
            'В продакшене рекомендуется ограничить доступ (IP, отдельный секрет) — сейчас поведение как в исходном API.'
        ),
        request=REQ_ADMIN_CREATE,
    )
    async def post(self, request):
        username = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''
        if not username or not password:
            raise ValidationError('username и password обязательны')
        admin = await sync_to_async(acc.create_admin)(username, password)
        return Response({'id': str(admin.id), 'username': admin.username})

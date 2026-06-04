"""Synchronous DB helpers for accounts (called via sync_to_async from async views)."""
from __future__ import annotations

import secrets
import string

import argon2
from django.core.mail import send_mail
from django.utils import timezone

from apps.common.media_urls import media_url
from apps.store_core.models import StoreAdmin, StoreUser

_ph = argon2.PasswordHasher()


def hash_user_password(raw: str) -> str:
    return _ph.hash(raw)


def verify_user_password(hash_str: str, raw: str) -> bool:
    try:
        _ph.verify(hash_str, raw)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


def hash_admin_password(raw: str) -> str:
    return _ph.hash(raw + 'dsjkh82&(78')


def verify_admin_password(hash_str: str, raw: str) -> bool:
    try:
        _ph.verify(hash_str, raw + 'dsjkh82&(78')
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False


def create_user(data: dict, avatar_file) -> StoreUser:
    if StoreUser.objects.filter(email=data['email']).exists():
        raise ValueError('Пользователь с таким email уже существует')
    pwd = hash_user_password(data['password'])
    user = StoreUser.objects.create(
        email=data['email'],
        first_name=data.get('firstName') or data.get('first_name'),
        last_name=data.get('lastName') or data.get('last_name'),
        middle_name=data.get('middleName') or data.get('middle_name'),
        phone=data.get('phone'),
        password=pwd,
    )
    if avatar_file:
        user.avatar = avatar_file
        user.save(update_fields=['avatar'])
    return user


def login_user(email: str, password: str) -> StoreUser:
    user = StoreUser.objects.filter(email=email).first()
    if not user:
        raise LookupError('Пользователь не найден')
    if not verify_user_password(user.password, password):
        raise ValueError('Неверный пароль')
    return user


def list_users_safe():
    rows = []
    for u in StoreUser.objects.all().order_by('created_at'):
        rows.append(
            {
                'id': str(u.id),
                'avatar': media_url(u.avatar),
                'createdAt': u.created_at,
                'email': u.email,
                'firstName': u.first_name,
                'lastName': u.last_name,
                'phone': u.phone,
                'updatedAt': u.updated_at,
            }
        )
    return rows


def get_user(pk: str) -> StoreUser | None:
    return StoreUser.objects.filter(pk=pk).first()


def delete_user(pk: str) -> None:
    StoreUser.objects.filter(pk=pk).delete()


def update_user(pk: str, data: dict, avatar_file) -> StoreUser:
    user = StoreUser.objects.get(pk=pk)
    if data.get('password'):
        user.password = hash_user_password(data['password'])
    if data.get('firstName') is not None:
        user.first_name = data['firstName']
    if data.get('lastName') is not None:
        user.last_name = data['lastName']
    if data.get('middleName') is not None:
        user.middle_name = data['middleName']
    if data.get('phone') is not None:
        user.phone = data['phone']
    if data.get('email') is not None:
        user.email = data['email']
    if avatar_file:
        user.avatar = avatar_file
    user.updated_at = timezone.now()
    user.save()
    return user


def change_avatar(pk: str, avatar_file) -> StoreUser:
    user = StoreUser.objects.get(pk=pk)
    user.avatar = avatar_file
    user.updated_at = timezone.now()
    user.save()
    return user


def change_password(pk: str, old: str, new: str) -> None:
    user = StoreUser.objects.get(pk=pk)
    if not verify_user_password(user.password, old):
        raise ValueError('Неверный пароль')
    user.password = hash_user_password(new)
    user.updated_at = timezone.now()
    user.save()


def reset_password(email_or_username: str) -> None:
    user = StoreUser.objects.filter(email=email_or_username).first()
    if not user:
        raise LookupError('Пользователь не найден')
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for _ in range(8))
    user.password = hash_user_password(new_password)
    user.updated_at = timezone.now()
    user.save()
    send_mail(
        subject='Новый пароль от вашего аккаунта',
        message=f'Ваш новый пароль: {new_password}',
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )


def create_admin(username: str, password: str) -> StoreAdmin:
    return StoreAdmin.objects.create(username=username, password=hash_admin_password(password))


def get_admin_by_username(username: str) -> StoreAdmin | None:
    return StoreAdmin.objects.filter(username=username).first()


def user_to_response(user: StoreUser) -> dict:
    return {
        'id': str(user.id),
        'firstName': user.first_name,
        'lastName': user.last_name,
        'middleName': user.middle_name,
        'email': user.email,
        'phone': user.phone,
        'avatar': media_url(user.avatar),
        'createdAt': user.created_at,
        'updatedAt': user.updated_at,
    }

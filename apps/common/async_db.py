"""ORM helpers for async DRF views (Daphne / ASGI)."""
from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from asgiref.sync import sync_to_async

F = TypeVar('F', bound=Callable)


def db_sync(func: F) -> F:
    """Run sync ORM code on a thread-sensitive connection (required under ASGI)."""
    return sync_to_async(func, thread_sensitive=True)  # type: ignore[return-value]


def db_sync_decorator(view_method):
    """Wrap an async view method that calls a single sync DB function."""

    @wraps(view_method)
    async def wrapper(self, request, *args, **kwargs):
        return await view_method(self, request, *args, **kwargs)

    return wrapper

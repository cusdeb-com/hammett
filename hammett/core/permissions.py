"""The module contains the implementation of the permissions mechanism."""

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from hammett.core.screen import Screen
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Handler, HandlerAlias, State


def apply_permission_to(handler: 'HandlerAlias') -> 'HandlerAlias':
    """Applies permissions to the specified handler."""

    from hammett.conf import settings

    handler_wrapped = cast('Handler', handler)
    for permission_path in reversed(settings.PERMISSIONS):
        permission: type['Permission'] = import_string(permission_path)
        permissions_ignored = getattr(handler_wrapped, 'permissions_ignored', None)
        permission_instance = permission()
        if permissions_ignored and permission_instance.class_uuid in permissions_ignored:
            continue

        handler_wrapped = permission_instance.check_permission(handler_wrapped)

    return cast('HandlerAlias', handler_wrapped)


def ignore_permissions(
    permissions: 'Iterable[type[Permission]]',
) -> 'Callable[[HandlerAlias], Handler]':
    """The decorator is intended for decorating handlers (Screen methods)
    to specify which permissions they are allowed to ignore.
    """

    def decorator(func: 'HandlerAlias') -> 'Handler':
        handler = cast('Handler', func)
        handler.permissions_ignored = [permission().class_uuid for permission in permissions]

        @wraps(handler)
        async def wrapper(*args: 'Any', **kwargs: 'Any') -> 'Any':
            return await handler(*args, **kwargs)

        return cast('Handler', wrapper)
    return decorator


class Permission(Screen):
    """The base class for the implementations of custom permissions."""

    def __init__(self: 'Self') -> None:
        if getattr(self, 'class_uuid', None) is None:
            self.class_uuid = uuid4()

        super().__init__()

    def check_permission(self: 'Self', handler: 'Handler') -> 'Handler':
        """Checks if there is a permission to invoke handlers (Screen methods).
        The method is invoked under the hood, so you should not run it directly.
        """

        @wraps(handler)
        async def wrapper(
            screen: 'Screen',
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> 'Any':
            if asyncio.iscoroutinefunction(self.has_permission):
                permitted = await self.has_permission(update, context)
            else:
                permitted = self.has_permission(update, context)

            if permitted:
                return await handler(screen, update, context)  # type: ignore[arg-type]

            return await self.handle_permission_denied(update, context)

        return cast('Handler', wrapper)

    async def handle_permission_denied(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoked in case of `has_permission` returns False."""

        raise NotImplementedError

    def has_permission(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'bool | Awaitable[bool]':
        """Invoked before running each Screen method to check a permission."""

        raise NotImplementedError

"""The module contains the implementation of the permissions mechanism."""

import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext._utils.types import BD, BT, CD, UD

from hammett.core.screen import Screen
from hammett.types import Stage
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Awaitable, Iterable

    from typing_extensions import Self

    from hammett.types import Handler


def apply_permission_to(
    handler: 'Callable[[Update, CallbackContext[BT, UD, CD, BD]], Coroutine[Any, Any, Stage]]',
) -> 'Callable[[Update, CallbackContext[BT, UD, CD, BD]], Coroutine[Any, Any, Stage]]':
    """Applies permissions to the specified handler."""

    from hammett.conf import settings

    handler_wrapped = handler
    for permission_path in settings.PERMISSIONS:
        permission: type['Permission'] = import_string(permission_path)
        permissions_ignored = getattr(handler_wrapped, 'permissions_ignored', None)
        permission_instance = permission()
        if permissions_ignored and permission_instance.class_uuid in permissions_ignored:
            continue

        handler_wrapped = permission_instance.check_permission(handler_wrapped)

    return handler_wrapped


def ignore_permissions(
    permissions: 'Iterable[type[Permission]]',
) -> 'Callable[[Handler[..., Stage]], Handler[..., Stage]]':
    """The decorator is intended for decorating handlers (Screen methods)
    to specify which permissions they are allowed to ignore.
    """

    def decorator(func: 'Handler[..., Stage]') -> 'Handler[..., Stage]':
        func.permissions_ignored = [permission().class_uuid for permission in permissions]

        @wraps(func)
        async def wrapper(
            self: 'Screen',
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
            *args: 'Any',
            **kwargs: 'Any',
        ) -> 'Stage':
            return await func(self, update, context, *args, **kwargs)

        return cast('Handler[..., Stage]', wrapper)
    return decorator


class Permission(Screen):
    """The base class for the implementations of custom permissions."""

    def __init__(self: 'Self') -> None:
        if getattr(self, 'class_uuid', None) is None:
            self.class_uuid = uuid4()

        super().__init__()

    def check_permission(
        self: 'Self',
        handler: Callable[[Update, CallbackContext[BT, UD, CD, BD]], Coroutine[Any, Any, Stage]],
    ) -> 'Callable[[Update, CallbackContext[BT, UD, CD, BD]], Coroutine[Any, Any, Stage]]':
        """Checks if there is a permission to invoke handlers (Screen methods).
        The method is invoked under the hood, so you should not run it directly.
        """

        @wraps(handler)
        async def wrapper(*args: 'Any', **kwargs: 'Any') -> 'Stage':
            if asyncio.iscoroutinefunction(self.has_permission):
                permitted = await self.has_permission(*args, **kwargs)
            else:
                permitted = self.has_permission(*args, **kwargs)

            if permitted:
                return await handler(*args, **kwargs)

            return await self.handle_permission_denied(*args, **kwargs)

        return wrapper

    async def handle_permission_denied(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Invoked in case of `has_permission` returns False."""

        raise NotImplementedError

    def has_permission(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'bool | Awaitable[bool]':
        """Invoked before running each Screen method to check a permission."""

        raise NotImplementedError

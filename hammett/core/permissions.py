"""The module contains the implementation of the permissions mechanism."""

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from hammett.core.screen import Screen

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Coroutine, Iterable
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Handler, Stage


def ignore_permissions(
    permissions: 'Iterable[type[Permission]]',
) -> 'Callable[[Handler[..., Stage]], Handler[..., Stage]]':
    """The decorator is intended for decorating handlers (Screen methods)
    to specify which permissions they are allowed to ignore.
    """

    def decorator(func: 'Handler[..., Stage]') -> 'Handler[..., Stage]':
        func.permissions_ignored = [permission.CLASS_UUID for permission in permissions]

        @wraps(func)
        async def wrapper(
            self: 'Screen',
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> 'Stage':
            return await func(self, update, context)

        return cast('Handler[..., Stage]', wrapper)
    return decorator


class Permission(Screen):
    """The base class for the implementations of custom permissions."""

    CLASS_UUID = uuid4()

    def check_permission(
        self: 'Self',
        handler: 'Handler[..., Stage]',
    ) -> 'Callable[[Update, CallbackContext[BT, UD, CD, BD]], Coroutine[Any, Any, Stage]]':
        """Checks if there is a permission to invoke handlers (Screen methods).
        The method is invoked under the hood, so you should not run it directly.
        """

        @wraps(handler)
        async def wrapper(
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> 'Stage':
            if asyncio.iscoroutinefunction(self.has_permission):
                permitted = await self.has_permission(update, context)
            else:
                permitted = self.has_permission(update, context)

            if permitted:
                return await handler(update, context)  # type: ignore[call-arg, arg-type]

            return await self.handle_permission_denied(update, context)

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

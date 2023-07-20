"""The module contains the implementation of the permissions mechanism. """

from functools import wraps
from typing import TYPE_CHECKING, cast
from uuid import uuid4

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Iterable
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.screen import Screen
    from hammett.types import Handler, Stage


async def ignore_permissions(
    permissions: 'Iterable[Permission]',
) -> 'Callable[[Handler[..., Stage]], Coroutine[Any, Any, Handler[..., Stage]]]':
    """The decorator is intended for decorating Screen methods to specify
    which permissions they are allowed to ignore.
    """

    async def decorator(func: 'Handler[..., Stage]') -> 'Handler[..., Stage]':
        func.permissions_ignored = [permission.CLASS_UUID for permission in permissions]

        @wraps(func)
        async def wrapper(
            self: 'Screen',
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> 'Stage':
            return func(self, update, context)

        return cast('Handler[..., Stage]', wrapper)
    return decorator


class Permission:
    """The base class for the implementations of custom permissions. """

    CLASS_UUID = uuid4()

    def check_permission(
        self: 'Self',
        handler: 'Handler[..., Stage]',
    ) -> 'Callable[[Screen, Update, CallbackContext[BT, UD, CD, BD]], Stage]':
        @wraps(handler)
        def wrapper(
            screen: 'Screen',
            update: 'Update',
            context: 'CallbackContext[BT, UD, CD, BD]',
        ) -> 'Stage':
            """"""

            if self.has_permission(update, context):
                return handler(screen, update, context)

            return self.handle_permission_denied(update, context)

        return wrapper

    def handle_permission_denied(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Invoked in case of `has_permission` returns False. """

        raise NotImplementedError

    def has_permission(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Invoked before running each Screen method to check a permission. """

        raise NotImplementedError

"""The module contains the implementation of the permissions mechanism. """

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import TYPE_CHECKING, cast
from uuid import uuid4

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Self

    from telegram import Update
    from telegram.ext import CallbackContext

    from hammett.types import Func, Handler


async def ignore_permissions(
    permissions: 'Iterable[Permission]',
) -> 'Callable[[Func], Coroutine[tuple, dict, Coroutine[Func]]]':
    """The decorator is intended for decorating Screen methods to specify
    which permissions they are allowed to ignore.
    """

    async def decorator(func: 'Func') -> 'Coroutine[Func]':
        func.permissions_ignored = [permission.CLASS_UUID for permission in permissions]

        @wraps(func)
        async def wrapper(*args: tuple, **kwargs: dict) -> 'Coroutine[Func]':
            return func(*args, **kwargs)

        return cast(Coroutine['Func'], wrapper)
    return decorator


class Permission:
    """The base class for the implementations of custom permissions. """

    CLASS_UUID = uuid4()

    async def check_permission(
        self: 'Self',
        handler: 'Handler',
    ) -> 'Callable[Coroutine[tuple, dict, Coroutine[Func]]]':
        @wraps(handler)
        async def wrapper(*args: tuple, **kwargs: dict) -> 'Coroutine[Func] | Coroutine[int]':
            """"""

            if self.has_permission(*args, **kwargs):
                res = handler(*args, **kwargs)
                return cast(Coroutine['Func'], res)

            return self.handle_permission_denied(*args, **kwargs)

        return wrapper

    async def handle_permission_denied(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext',
    ) -> int:
        """Invoked in case of `has_permission` returns False. """

        raise NotImplementedError

    async def has_permission(self: 'Self', update: 'Update', context: 'CallbackContext') -> bool:
        """Invoked before running each Screen method to check a permission. """

        raise NotImplementedError

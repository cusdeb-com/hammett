"""The module contains utils for writing tests. """

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, cast

from hammett.conf import GlobalSettings, settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from types import TracebackType
    from typing import Any

    from typing_extensions import Self

    from hammett.types import Func


class TestContextDecorator:
    """A base class that can be used as
    1) a context manager during tests
    2) a test function
    3) unittest.TestCase subclass decorator to perform temporary alterations
       of the settings.

    `kwarg_name`: keyword argument passing the return value of enable() when
                  used as a function decorator.
    """

    def __init__(self: 'Self', kwarg_name: str | None = None) -> None:
        self.kwarg_name = kwarg_name

    def __enter__(self: 'Self') -> 'Any':
        return self.enable()

    def __exit__(
        self: 'Self',
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: 'TracebackType | None',
    ) -> None:
        self.disable()

    def enable(self: 'Self') -> 'Any':
        raise NotImplementedError

    def disable(self: 'Self') -> 'Any':
        raise NotImplementedError

    def decorate_callable(self: 'Self', func: 'Func') -> 'Callable[..., Any | Awaitable[Any]]':
        if asyncio.iscoroutinefunction(func):
            # If the inner function is an async function, we must execute async
            # as well so that the `with` statement executes at the right time.
            @wraps(func)
            async def inner(*args: tuple['Any'], **kwargs: dict[str, 'Any']) -> 'Any':
                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context

                    return await func(*args, **kwargs)
        else:
            @wraps(func)
            def inner(*args: tuple['Any'], **kwargs: dict[str, 'Any']) -> 'Any':
                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context

                    return func(*args, **kwargs)

        return inner

    def __call__(self: 'Self', decorated: 'Func') -> 'Callable[..., Any] | Awaitable[Any]':
        if callable(decorated):
            return self.decorate_callable(decorated)

        msg = f'Cannot decorate object of type {type(decorated)}'
        raise TypeError(msg)


class override_settings(TestContextDecorator):  # noqa: N801
    """Decorates tests to perform temporary alterations of the settings. """

    def __init__(self: 'Self', **kwargs: dict[str, 'Any']) -> None:
        self.options = kwargs
        self.wrapped: 'GlobalSettings | None' = None
        super().__init__()

    def enable(self: 'Self') -> None:
        overriden_settings = GlobalSettings()
        for key, new_value in self.options.items():
            setattr(overriden_settings, key, new_value)

        self.wrapped = cast('GlobalSettings', settings._wrapped)  # noqa: SLF001
        settings._wrapped = overriden_settings  # noqa: SLF001
        for key, new_value in self.options.items():
            setattr(settings, key, new_value)

    def disable(self: 'Self') -> None:
        settings._wrapped = self.wrapped  # noqa: SLF001
        del self.wrapped

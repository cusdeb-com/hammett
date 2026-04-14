# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The module contains utils for writing tests."""

import asyncio
from functools import wraps
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock, patch

from hammett.conf import GlobalSettings, settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from types import TracebackType
    from typing import Any, Self

    from hammett.core.constants import FinalRenderConfig
    from hammett.types.core import Func


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
        """Initialize a test context decorator object."""
        self.kwarg_name = kwarg_name

    def __enter__(self: 'Self') -> 'Any':
        """Invoke when execution enters the context of the with statement.

        Returns:
            Call to the `enable` method.

        """
        return self.enable()

    def __exit__(
        self: 'Self',
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: 'TracebackType | None',  # noqa: PYI036
    ) -> None:
        """Invoke when execution leaves the context of the with statement."""
        self.disable()

    def enable(self: 'Self') -> 'Any':
        """Invoke when execution enters the context of the with statement."""
        raise NotImplementedError

    def disable(self: 'Self') -> 'Any':
        """Invoke when execution leaves the context of the with statement."""
        raise NotImplementedError

    def decorate_callable(self: 'Self', func: 'Func') -> 'Callable[..., Any | Awaitable[Any]]':
        """Decorate either a coroutine or a function.

        Returns:
            Decorated coroutine or function.

        """
        if asyncio.iscoroutinefunction(func):
            # If the inner function is an async function, we must execute async
            # as well so that the `with` statement executes at the right time.
            @wraps(func)
            async def inner(*args: 'Any', **kwargs: 'Any') -> 'Any':
                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context

                    return await func(*args, **kwargs)
        else:

            @wraps(func)
            def inner(*args: 'Any', **kwargs: 'Any') -> 'Any':
                with self as context:
                    if self.kwarg_name:
                        kwargs[self.kwarg_name] = context

                    return func(*args, **kwargs)

        return inner

    def __call__(self: 'Self', decorated: 'Func') -> 'Callable[..., Any] | Awaitable[Any]':
        """Wrap the specified coroutine or function, and invoke the decorator.

        Returns:
            Wrapped specified coroutine or function.

        Raises:
            TypeError: If the provided type of object is not callable.

        """
        if callable(decorated):
            return self.decorate_callable(decorated)

        msg = f'Cannot decorate object of type {type(decorated)}'
        raise TypeError(msg)


class catch_render_config(TestContextDecorator):  # noqa: N801
    """The class implements a decorator to capture the value of `RenderConfig`."""

    def __init__(self: 'Self') -> None:
        """Initialize a patcher for the `FinalRenderConfig` state hook."""
        self.hook_patcher = patch('hammett.test.utils.hook_final_render_config')
        self.mock: MagicMock | AsyncMock | None = None

        super().__init__(kwarg_name='actual')

    def enable(self: 'Self') -> 'Self':
        """Invoke when execution enters the context of the `with` statement.

        Returns:
            Instance of the catch_render_config.

        """
        self.mock = self.hook_patcher.start()
        return self

    def disable(self: 'Self') -> None:
        """Invoke when execution leaves the context of the `with` statement."""
        self.hook_patcher.stop()

    @property
    def final_render_config(self) -> 'FinalRenderConfig | None':
        """Return `FinalRenderConfig` that was used for the screen render."""
        if not self.mock:
            return None

        try:
            config: FinalRenderConfig = self.mock.call_args[0][0]
        except (TypeError, IndexError, AttributeError):
            return None
        else:
            return config


class override_settings(TestContextDecorator):  # noqa: N801
    """Decorate tests to perform temporary alterations of the settings."""

    def __init__(self: 'Self', **kwargs: 'Any') -> None:
        """Initialize an overrider settings object."""
        self.options = kwargs
        self.wrapped: GlobalSettings | None = None
        super().__init__()

    def enable(self: 'Self') -> None:
        """Invoke when execution enters the context of the with statement."""
        overriden_settings = GlobalSettings()
        for key, new_value in self.options.items():
            setattr(overriden_settings, key, new_value)

        self.wrapped = cast('GlobalSettings', settings._wrapped)  # noqa: SLF001
        settings._wrapped = overriden_settings  # noqa: SLF001
        for key, new_value in self.options.items():
            setattr(settings, key, new_value)

    def disable(self: 'Self') -> None:
        """Invoke when execution leaves the context of the with statement."""
        settings._wrapped = self.wrapped  # noqa: SLF001
        del self.wrapped


async def hook_final_render_config(_final_config: 'FinalRenderConfig') -> None:
    """Doesn't do anything. It's replaced with a mock during tests and
    captures the final render config.
    """

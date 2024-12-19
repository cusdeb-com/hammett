"""The module contains the implementation of a modified `EventLoopPolicy` that can track the time
of select.
"""

import asyncio
import selectors
import time
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from asyncio.selector_events import BaseSelectorEventLoop
    from selectors import SelectorKey
    from typing import Any


class StopWatchSelector(selectors.DefaultSelector):
    """The class implements the tracking of the time of retrieving the task from the event loop."""

    def __init__(self, *args: 'Any', **kwargs: 'Any') -> None:
        """Initialize the `select_time` attribute."""
        self.select_time = 0.0

        super().__init__(*args, **kwargs)

    def reset_select_time(self) -> None:
        """Reset the `select_time` attribute value."""
        self.select_time = 0.0

    def select(self, timeout: float | None = None) -> 'list[tuple[SelectorKey, int]]':
        """Track select time if timeout is greater than zero.

        Returns:
            List of tuples, one for each ready file object.

        """
        if timeout is not None and timeout <= 0:
            return super().select(timeout)

        start = time.time()
        try:
            return super().select(timeout)
        finally:
            self.select_time += time.time() - start


class StopWatchEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """The class implements `StopWatchSelector` passing in the event loop."""

    def new_event_loop(self) -> 'BaseSelectorEventLoop':
        """Create a new event loop and pass `StopWatchSelector` into it.

        Returns:
            New event loop.

        """
        selector = StopWatchSelector()
        return cast(
            'BaseSelectorEventLoop',
            self._loop_factory(selector=selector),  # type: ignore[attr-defined]
        )

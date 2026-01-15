"""The module contains classes that implement handler stats processing."""

import json
import platform
from hashlib import md5
from pathlib import Path
from typing import TYPE_CHECKING

from hammett.core.handlers import get_handler_name

if TYPE_CHECKING:
    from hammett.core.constants import HandlerStats
    from hammett.types import Handler, StopwatchStats


def get_full_platform() -> tuple[str, str, str]:
    """Return info about the current platform.

    Returns
    -------
        Information about the current platform.

    """
    return platform.python_version(), platform.python_implementation(), platform.platform()


class BaseStatsProcessor:
    """The base class for implementing handler stats processing."""

    def __init__(self, handler: 'Handler', stats: 'HandlerStats') -> None:
        """Save `handler` and `stats` values to the relevant attributes."""
        self.handler = handler
        self.stats = stats

    @classmethod
    async def on_exit(cls) -> None:
        """Run after application is stopped."""

    async def process(self) -> None:
        """Run after handler is called and statistics are retrieved."""
        raise NotImplementedError


class PrintStatsProcessor(BaseStatsProcessor):
    """The class implements the output of the handler stats via a print function."""

    async def process(self) -> None:
        """Print handler stats."""
        msg = (
            f'{get_handler_name(self.handler)}:\n'
            f'  CPU time: {self.stats["cpu_time"]}\n'
            f'  Select time: {self.stats["select_time"]}\n'
            f'  Other IO time: {self.stats["other_io_time"]}\n'
            f'  Real time: {self.stats["real_time"]}\n'
        )
        print(msg)  # noqa: T201


class JsonStatsProcessor(BaseStatsProcessor):
    """The class collects the stats from all handlers and dumps them into a JSON file."""

    _all_stats: 'StopwatchStats' = {}

    async def process(self) -> None:
        """Add handler stats to all stats dict."""
        handler_name = get_handler_name(self.handler)
        try:
            self._all_stats[handler_name]
        except KeyError:
            self._all_stats[handler_name] = []

        self._all_stats[handler_name].append(self.stats)

    @classmethod
    async def on_exit(cls) -> None:
        """Dump the accumulated stats into a file."""
        platform_name = ';'.join(get_full_platform())
        file_name = f'handler-stats-{md5(platform_name.encode()).hexdigest()}.json'  # noqa: S324
        stats_to_dump = (platform_name, cls._all_stats)

        # we can't use async writing to a file because it won't execute in time
        with Path(file_name).open('w', encoding='utf-8') as f:  # noqa: ASYNC230
            json.dump(stats_to_dump, f, ensure_ascii=False, indent=4)

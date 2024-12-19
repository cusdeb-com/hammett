"""The module contains a decorator that wraps handlers to track their execution time."""

import asyncio
import functools
import logging
import time
from typing import TYPE_CHECKING

from hammett.conf import settings
from hammett.core.exceptions import ImproperlyConfigured
from hammett.stopwatch.event_loop import StopWatchSelector
from hammett.utils.handler import wraps_handler
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from typing import Any

    from hammett.core.constants import HandlerStats
    from hammett.stopwatch.stats import BaseStatsProcessor
    from hammett.types import Handler

LOGGER = logging.getLogger(__name__)


@functools.cache
def get_stopwatch_stats_processor() -> 'type[BaseStatsProcessor]':
    """Import a stopwatch stats processor from a specified path in
    the `STOPWATCH_STATS_PROCESSOR` setting and return it.

    Returns:
        Stopwatch stats processor.

    Raises:
        ImproperlyConfigured: If it's not possible to import the stopwatch stats processor.

    """
    try:
        processor = import_string(settings.STOPWATCH_STATS_PROCESSOR)
    except ImportError as exc:
        msg = (
            f'The module could not be imported: {settings.STOPWATCH_STATS_PROCESSOR}. '
            f'Check your STOPWATCH_STATS_PROCESSOR setting.'
        )
        raise ImproperlyConfigured(msg) from exc
    else:
        return processor


def collect_handler_stats(func: 'Handler') -> 'Handler':
    """Collect the stats from the handler and pass them to `STOPWATCH_STATS_PROCESSOR`.

    Returns
    -------
        Wrapped handler.

    """
    stats_processor = get_stopwatch_stats_processor()

    @wraps_handler(func)
    async def wrapper(*args: 'Any', **kwargs: 'Any') -> 'Any':
        event_loop_selector = getattr(asyncio.get_event_loop(), '_selector', None)
        if event_loop_selector is None or not isinstance(event_loop_selector, StopWatchSelector):
            is_possible_get_select_time = False
            LOGGER.error(
                'Unable to retrieve select time stats. Did you change the event loop policy?',
            )
        else:
            is_possible_get_select_time = True
            event_loop_selector.reset_select_time()

        real_time = time.time()
        process_time = time.process_time()

        response = await func(*args, **kwargs)

        real_time = time.time() - real_time
        cpu_time = time.process_time() - process_time

        select_time = event_loop_selector.select_time if (
            event_loop_selector and is_possible_get_select_time
        ) else 0.0
        other_io_time = max(0.0, real_time - cpu_time - select_time)

        stats: HandlerStats = {
            'cpu_time': cpu_time,
            'select_time': select_time,
            'other_io_time': other_io_time,
            'real_time': real_time,
        }
        await stats_processor(func, stats).process()

        return response

    return wrapper

"""The package contains functions to collect handler stats and represents them further."""

__all__ = (
    'StopWatchEventLoopPolicy',
    'StopWatchSelector',
    'collect_handler_stats',
    'get_stopwatch_stats_processor',
)

from hammett.stopwatch.collector import collect_handler_stats, get_stopwatch_stats_processor
from hammett.stopwatch.event_loop import StopWatchEventLoopPolicy, StopWatchSelector

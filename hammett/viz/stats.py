"""The module contains methods for working with handler statistics."""

import statistics
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

    from hammett.types import StopwatchStats
    from hammett.viz.types import AverageStats


def avg_stats_table_rows(stats: 'AverageStats') -> str:
    """Return the table columns from the arithmetic mean values of the handler statistics.

    Returns
    -------
        Table columns from the arithmetic mean values of the handler statistics.

    """
    rows = ''
    for stat_row in stats:
        nested_rows = ''
        for stat in stat_row:
            nested_rows += f'<td>{stat}</td>\n'

        rows += f'<tr>{nested_rows}</tr>\n'

    return rows


class Stats:
    """The class contains methods for handling handler statistics."""

    def __init__(self, stats: 'StopwatchStats') -> None:
        """Save handler statistics."""
        self.stats: Final[StopwatchStats] = stats

    @cached_property
    def avg_stats(self) -> 'AverageStats':
        """Return the arithmetic mean for each statistic for each handler."""
        avg_stats = []
        for handler_name, stats in self.stats.items():
            cpu_stats = []
            select_stats = []
            other_io_stats = []
            real_stats = []
            for stat in stats:
                cpu_stats.append(stat.get('cpu_time', 0.0))
                select_stats.append(stat.get('select_time', 0.0))
                other_io_stats.append(stat.get('other_io_time', 0.0))
                real_stats.append(stat.get('real_time', 0.0))

            avg_stats.append((
                handler_name,
                statistics.fmean(cpu_stats),
                statistics.fmean(select_stats),
                statistics.fmean(other_io_stats),
                statistics.fmean(real_stats),
            ))

        return avg_stats

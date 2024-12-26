"""The module contains methods for working with handler statistics."""

import json
import re
import statistics
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

    from hammett.types import StopwatchStats
    from hammett.viz.types import AverageStats


def detect_stats_files(directory: 'Path') -> 'list[Path]':
    """Detect files with stats and returns them.

    Returns
    -------
        Files with stats.

    """
    return [
        stat_file for stat_file in directory.iterdir()
        if stat_file.is_file() and re.match(r'^handler-stats-\w{32}\.json', stat_file.name)
    ]


def get_platforms(file_paths: 'list[Path]') -> 'dict[str, tuple[str, Path]]':
    """Return dict with a hash from filename, platform and a file that
    contains stats for it.

    Returns
    -------
        FileNotFoundError: If the template is not loaded.

    """
    platforms = {}
    for file_path in file_paths:
        stat = Stats(file_path).load()
        platforms.update({stat.filename_hash(): (stat.platform, file_path)})

    return platforms


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

    def __init__(self, file_path: 'Path') -> None:
        """Save the path to the handler statistics file."""
        self.file_path: Final[Path] = file_path
        self.platform = ''
        self.stats: StopwatchStats | None = None

    def load(self) -> 'Stats':
        """Load the stats file.

        Returns
        -------
            Stats instance.

        """
        with self.file_path.open('r', encoding='utf-8') as f:
            stats = json.load(f)
            self.platform = stats[0]
            self.stats = stats[1]

        return self

    def filename_hash(self) -> str:
        """Return hash from filename.

        Returns
        -------
            Hash from filename.

        """
        return cast('str', re.findall(r'\w{32}', self.file_path.name)[0])

    def avg_stats(self) -> 'AverageStats':
        """Return the arithmetic mean for each statistic for each handler.

        Returns:
            Arithmetic mean for each statistic for each handler.

        Raises:
            FileNotFoundError: If the stats file is not loaded.

        """
        if not self.stats:
            msg = 'Stats file is not loaded'
            raise FileNotFoundError(msg)

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

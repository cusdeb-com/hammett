"""The module contains tests for stopwatch stats collection."""

from types import SimpleNamespace
from unittest.mock import patch

from hammett.core.exceptions import ImproperlyConfigured
from hammett.stopwatch.collector import collect_handler_stats, get_stopwatch_stats_processor
from hammett.stopwatch.event_loop import StopWatchSelector
from hammett.stopwatch.stats import BaseStatsProcessor, PrintStatsProcessor
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings


class _CapturingStatsProcessor(BaseStatsProcessor):
    """The class captures handler stats for assertions."""

    captured_stats: list[dict[str, float]] = []

    @classmethod
    def reset(cls) -> None:
        """Clear captured stats before each test."""
        cls.captured_stats = []

    async def process(self):
        """Capture stats for assertions."""
        self.__class__.captured_stats.append(self.stats)


class StopWatchCollectorTests(BaseTestCase):
    """The class implements tests for the stopwatch collector."""

    def setUp(self):
        """Reset cached processor before each test."""
        get_stopwatch_stats_processor.cache_clear()
        _CapturingStatsProcessor.reset()
        super().setUp()

    async def test_collect_handler_stats_logs_when_selector_unavailable(self):
        """Test logging when select time cannot be retrieved."""

        async def handler():  # noqa: RUF029
            """Represent a stub handler for the testing purposes."""
            return 'response'

        with (
            patch(
                'hammett.stopwatch.collector.get_stopwatch_stats_processor',
                return_value=_CapturingStatsProcessor,
            ),
            patch(
                'hammett.stopwatch.collector.asyncio.get_event_loop',
                return_value=SimpleNamespace(_selector=None),
            ),
            self.assertLogs('hammett.stopwatch.collector', level='ERROR') as log,
        ):
            wrapped_handler = collect_handler_stats(handler)
            response = await wrapped_handler()

        self.assertEqual(response, 'response')
        self.assertEqual(len(log.records), 1)
        self.assertTrue(_CapturingStatsProcessor.captured_stats)

        stats = _CapturingStatsProcessor.captured_stats[-1]

        self.assertEqual(stats['select_time'], 0.0)
        self.assertGreater(stats['cpu_time'], 0.0)
        self.assertGreater(stats['other_io_time'], 0.0)
        self.assertGreater(stats['real_time'], 0.0)

    async def test_collect_handler_stats_uses_selector_select_time(self):
        """Test select time usage when the selector supports tracking."""
        selector = StopWatchSelector()

        async def handler():  # noqa: RUF029
            """Represent a stub handler for the testing purposes."""
            selector.select_time = 1.5
            return 'response'

        with patch.object(
            selector,
            'reset_select_time',
            wraps=selector.reset_select_time,
        ) as mock_reset_select_time, patch(
            'hammett.stopwatch.collector.get_stopwatch_stats_processor',
            return_value=_CapturingStatsProcessor,
        ), patch(
            'hammett.stopwatch.collector.asyncio.get_event_loop',
            return_value=SimpleNamespace(_selector=selector),
        ), patch(
            'hammett.stopwatch.collector.time.time',
            side_effect=[20.0, 26.0, 26.0],
        ), patch(
            'hammett.stopwatch.collector.time.process_time',
            side_effect=[4.0, 6.0, 6.0],
        ), self.assertNoLogs('hammett.stopwatch.collector', level='ERROR'):
            wrapped_handler = collect_handler_stats(handler)
            response = await wrapped_handler()

        self.assertEqual(response, 'response')
        mock_reset_select_time.assert_called_once()
        self.assertTrue(_CapturingStatsProcessor.captured_stats)

        stats = _CapturingStatsProcessor.captured_stats[-1]
        self.assertEqual(stats['cpu_time'], 2.0)
        self.assertEqual(stats['select_time'], 1.5)
        self.assertEqual(stats['other_io_time'], 2.5)
        self.assertEqual(stats['real_time'], 6.0)

    @override_settings(STOPWATCH_STATS_PROCESSOR='hammett.stopwatch.stats.MissingProcessor')
    def test_get_stopwatch_stats_processor_raises_on_invalid_path(self):
        """Test raising ImproperlyConfigured for invalid processor paths."""
        with self.assertRaises(ImproperlyConfigured) as ctx:
            get_stopwatch_stats_processor()

        self.assertIn('Check your STOPWATCH_STATS_PROCESSOR setting', str(ctx.exception))

    @override_settings(STOPWATCH_STATS_PROCESSOR='hammett.stopwatch.stats.PrintStatsProcessor')
    def test_get_stopwatch_stats_processor_returns_configured_class(self):
        """Test returning the configured stats processor class."""
        actual = get_stopwatch_stats_processor()
        self.assertIs(actual, PrintStatsProcessor)

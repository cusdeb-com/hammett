"""The module contains tests for stopwatch event loop components."""

from unittest.mock import patch

from hammett.stopwatch.event_loop import StopWatchEventLoopPolicy, StopWatchSelector
from hammett.test.base import BaseTestCase


class StopWatchEventLoopPolicyTests(BaseTestCase):
    """The class implements tests for the stopwatch event loop policy."""

    def test_new_event_loop_uses_stopwatch_selector(self):
        """Test that a new event loop uses StopWatchSelector."""
        policy = StopWatchEventLoopPolicy()
        loop = policy.new_event_loop()
        try:
            self.assertIsInstance(loop._selector, StopWatchSelector)  # noqa: SLF001
        finally:
            loop.close()


class StopWatchSelectorTests(BaseTestCase):
    """The class implements tests for the stopwatch selector."""

    def test_reset_select_time_sets_to_zero(self):
        """Test resetting the select_time attribute."""
        selector = StopWatchSelector()
        selector.select_time = 2.0

        selector.reset_select_time()

        self.assertEqual(selector.select_time, 0.0)

    def test_select_does_not_track_when_timeout_zero(self):
        """Test select does not track time when timeout is zero."""
        selector = StopWatchSelector()
        selector.select_time = 1.0

        with patch(
            'hammett.stopwatch.event_loop.selectors.DefaultSelector.select',
            return_value=[],
        ):
            selector.select(timeout=0)

        self.assertEqual(selector.select_time, 1.0)

    def test_select_tracks_time_when_timeout_positive(self):
        """Test select tracks time when timeout is positive."""
        selector = StopWatchSelector()
        with (
            patch('hammett.stopwatch.event_loop.selectors.DefaultSelector.select', return_value=[]),
            patch('hammett.stopwatch.event_loop.time.time', side_effect=[1.0, 3.0]),
        ):
            selector.select(timeout=1.0)

        self.assertEqual(selector.select_time, 2.0)

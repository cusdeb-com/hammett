"""The module contains tests for bot stopwatch setup and teardown."""

# ruff: noqa: S106, SLF001

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from hammett.core.bot import Bot
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import get_bot


class BotStopWatchTests(BaseTestCase):
    """The class implements tests for bot stopwatch setup and teardown."""

    @override_settings(HANDLERS_STOPWATCH=True)
    async def test_post_stop_calls_stats_processor_on_exit_when_enabled(self):
        """Test post_stop calls stats processor on_exit when stopwatch is enabled."""
        mock_processor = MagicMock()
        mock_processor.on_exit = AsyncMock()

        with patch(
            'hammett.stopwatch.get_stopwatch_stats_processor',
            return_value=mock_processor,
        ):
            await Bot.post_stop(SimpleNamespace())

        mock_processor.on_exit.assert_awaited_once()

    @override_settings(HANDLERS_STOPWATCH=False)
    async def test_post_stop_does_not_call_stats_processor_when_disabled(self):
        """Test post_stop does not use stats processor when stopwatch is disabled."""
        with patch('hammett.stopwatch.get_stopwatch_stats_processor') as mock_get_processor:
            self.assertIsNone(await Bot.post_stop(SimpleNamespace()))
            mock_get_processor.assert_not_called()

    @override_settings(HANDLERS_STOPWATCH=True, TOKEN='secret')
    def test_register_handlers_calls_collect_handler_stats_when_enabled(self):
        """Test _register_handlers calls collect_handler_stats when stopwatch is enabled."""
        with patch('hammett.stopwatch.collect_handler_stats') as mock_collect_handler_stats:
            mock_collect_handler_stats.side_effect = lambda handler: handler

            get_bot()

        mock_collect_handler_stats.assert_called()

    @override_settings(HANDLERS_STOPWATCH=False, TOKEN='secret')
    def test_setup_does_not_set_event_loop_policy_when_disabled(self):
        """Test _setup skips setting the event loop policy when disabled."""
        bot = get_bot()

        with (
            patch('hammett.core.bot.configure_logging') as mock_configure_logging,
            patch('hammett.core.bot.asyncio.set_event_loop_policy') as mock_set_policy,
        ):
            bot._setup()

        mock_configure_logging.assert_called_once()
        mock_set_policy.assert_not_called()

    @override_settings(HANDLERS_STOPWATCH=True, TOKEN='secret')
    def test_setup_sets_event_loop_policy_when_stopwatch_enabled(self):
        """Test _setup sets event loop policy when stopwatch is enabled."""
        bot = get_bot()

        with (
            patch('hammett.core.bot.configure_logging') as mock_configure_logging,
            patch('hammett.stopwatch.StopWatchEventLoopPolicy') as mock_policy_class,
            patch('hammett.core.bot.asyncio.set_event_loop_policy') as mock_set_policy,
        ):
            mock_policy_instance = mock_policy_class.return_value
            bot._setup()

        mock_configure_logging.assert_called_once()
        mock_set_policy.assert_called_once_with(mock_policy_instance)

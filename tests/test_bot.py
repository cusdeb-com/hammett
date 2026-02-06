"""The module contains the tests for the bot."""

# ruff: noqa: RUF029, S106, PT019, SLF001

import logging
import re
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters

from hammett.core.bot import Bot
from hammett.core.button import Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.exceptions import (
    CallbackNotProvidedError,
    JobKwargsNotProvidedError,
    TokenIsNotSpecifiedError,
    UnknownHandlerTypeError,
)
from hammett.core.handlers import calc_checksum
from hammett.core.mixins import RouteMixin
from hammett.core.persistence import RedisPersistence
from hammett.error_handler import default_error_handler
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from hammett.types.core import HandlerType, State
from tests.base import (
    BOT_TEST_NAME,
    BaseTestScreenWithDescription,
    TestScreen,
    TestStartScreen,
    get_bot,
)

_NEW_STATE = State('1')

_TEST_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname}: {name}: {asctime}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'formatter': 'standard',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'hammett_test': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


async def _test_error_handler(_update, _context):
    """Represent a stub error_handler for the testing purposes."""
    return


async def _test_job(_context):
    """Represent a stub job for the testing purposes."""
    return DEFAULT_STATE


class TestRouteScreen(RouteMixin):
    """The class implements a screen with a routes attribute."""

    routes = (({DEFAULT_STATE}, _NEW_STATE),)


class TestScreenWithKeyboard(BaseTestScreenWithDescription):
    """The class implements the screen to test starting a bot."""

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [
            [
                Button('⬅️ Main Menu', TestStartScreen, source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
        ]


class BotTests(BaseTestCase):  # noqa: PLR0904
    """The class implements the tests for the bot."""

    def test_bot_initialization_with_persistence_specified(self):
        """Test a bot initialization with a persistence specified."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            persistence=RedisPersistence(),
        )

        assert bot._native_application.persistence is not None
        assert isinstance(bot._native_application.persistence, RedisPersistence)

    @override_settings(LOGGING=_TEST_LOGGING, TOKEN='secret-token')
    def test_bot_initialization_with_logging_setup(self):
        """Test the case when a bot is initialized with
        an overriden LOGGING setting.
        """
        get_bot()
        assert logging.root.manager.loggerDict['hammett_test'].getEffectiveLevel() == logging.INFO

    def test_bot_initialization_without_persistence_specified(self):
        """Test a bot initialization without a persistence specified."""
        bot = get_bot()
        assert bot._native_application.persistence is None

    def test_creating_button_handler(self):
        """Test creating CallbackQueryHandler for the button handler type."""
        mock_handler = MagicMock()
        mock_handler.__qualname__ = 'mock_handler'
        mock_possible_handler = MagicMock()

        handler_object = Bot._get_handler_object(
            mock_handler,
            HandlerType.BUTTON_HANDLER,
            mock_possible_handler,
        )

        assert isinstance(handler_object, CallbackQueryHandler)
        assert handler_object.callback == mock_handler
        assert handler_object.pattern.pattern == calc_checksum(mock_handler)

    def test_creating_command_handler(self):
        """Test creating MessageHandler for the command handler type."""
        mock_handler = MagicMock()
        mock_possible_handler = MagicMock()
        mock_possible_handler.command_name = 'start'

        handler_object = Bot._get_handler_object(
            mock_handler,
            HandlerType.COMMAND_HANDLER,
            mock_possible_handler,
        )

        assert isinstance(handler_object, MessageHandler)
        assert handler_object.callback == mock_handler

    def test_creating_input_handler(self):
        """Test creating MessageHandler for the input handler type."""
        mock_handler = MagicMock()
        mock_possible_handler = MagicMock()
        mock_possible_handler.filters = filters.TEXT

        handler_object = Bot._get_handler_object(
            mock_handler,
            HandlerType.INPUT_HANDLER,
            mock_possible_handler,
        )

        assert isinstance(handler_object, MessageHandler)
        assert handler_object.callback == mock_handler
        assert handler_object.filters is filters.TEXT

    def test_creating_typing_handler(self):
        """Test creating MessageHandler for the typing handler type."""
        mock_handler = MagicMock()
        mock_possible_handler = MagicMock()

        handler_object = Bot._get_handler_object(
            mock_handler,
            HandlerType.TYPING_HANDLER,
            mock_possible_handler,
        )

        assert isinstance(handler_object, MessageHandler)
        assert handler_object.callback == mock_handler
        assert handler_object.filters.name == (filters.TEXT & ~filters.COMMAND).name

    def test_registering_job_without_callback_specified(self):
        """Test registering a job without `callback` key specified."""
        with self.assertRaises(CallbackNotProvidedError):
            Bot(
                BOT_TEST_NAME,
                entry_point=TestStartScreen,
                job_configs=[
                    {
                        'job_kwargs': {'trigger': 'interval'},
                    },
                ],
            )

    def test_registering_job_without_job_kwargs_specified(self):
        """Test registering a job without `job_kwargs` key specified."""
        with self.assertRaises(JobKwargsNotProvidedError):
            Bot(
                BOT_TEST_NAME,
                entry_point=TestStartScreen,
                job_configs=[
                    {
                        'callback': _test_job,
                    },
                ],
            )

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_TIMED_OUT': True}, TOKEN='secret-token')
    def test_registering_default_error_handler_along_with_extra_one(self):
        """Test registering `default_error_handler` along with extra one,
        including the registering order.
        """
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            error_handlers=[_test_error_handler],
        )

        registered_error_handlers = list(bot._native_application.error_handlers)
        assert registered_error_handlers[0] == _test_error_handler
        assert registered_error_handlers[1] == default_error_handler

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_TIMED_OUT': True}, TOKEN='secret-token')
    def test_registering_default_error_handler_only(self):
        """Test registering `default_error_handler` only."""
        bot = get_bot()
        registered_error_handler = next(iter(bot._native_application.error_handlers))

        assert registered_error_handler == default_error_handler

    def test_registering_route_handlers(self):
        """Test registering route handlers."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            states={
                DEFAULT_STATE: {TestScreen},
                _NEW_STATE: {TestRouteScreen},
            },
        )

        jump_along_route_callback = bot._native_states[DEFAULT_STATE][2].callback
        assert jump_along_route_callback == TestRouteScreen().jump_along_route

        move_along_route_callback = bot._native_states[DEFAULT_STATE][3].callback
        assert move_along_route_callback == TestRouteScreen().move_along_route

    @patch('hammett.core.bot.HammettTranslation')
    def test_run_with_polling_mode(self, _mock_translation):
        """Test running bot in polling mode when USE_WEBHOOK is False."""
        bot = get_bot()
        with (
            patch.object(bot, '_native_application') as mock_native_application,
            patch.object(mock_native_application, 'run_polling') as mock_run_polling,
        ):
            bot.run()

            mock_run_polling.assert_called_once_with(allowed_updates=Update.ALL_TYPES)

    @override_settings(
        TOKEN='secret-token',
        USE_WEBHOOK=True,
        WEBHOOK_URL='https://test.com/webhook',
        WEBHOOK_URL_PATH='/webhook',
    )
    @patch('hammett.core.bot.HammettTranslation')
    def test_run_with_webhook_mode(self, _mock_translation):
        """Test running bot in webhook mode when USE_WEBHOOK is True."""
        bot = get_bot()
        with (
            patch.object(bot, '_native_application') as mock_native_application,
            patch.object(mock_native_application, 'run_webhook') as mock_run_webhook,
        ):
            bot.run()

            mock_run_webhook.assert_called_once()
            call_kwargs = mock_run_webhook.call_args.kwargs
            expected_port = 80
            assert call_kwargs['listen'] == '127.0.0.1'
            assert call_kwargs['port'] == expected_port
            assert call_kwargs['url_path'] == '/webhook'
            assert call_kwargs['webhook_url'] == 'https://test.com/webhook'
            assert 'allowed_updates' in call_kwargs

    @override_settings(TOKEN='secret-token')
    @patch('hammett.core.bot.HammettTranslation')
    def test_run_with_python_version_warning(self, _mock_translation):
        """Test that no warning is logged for safe Python versions."""
        bot = get_bot()

        mock_version = SimpleNamespace()
        mock_version.minor = 11
        mock_version.micro = 5  # unsafe version

        with (
            patch('sys.version_info', mock_version),
            patch.object(bot, '_native_application', MagicMock()),
            self.assertLogs('hammett.core.bot', level='WARNING') as log,
        ):
            bot.run()

            assert len(log.records) == 1
            assert (
                "It's recommended to avoid using the following versions of Python"
                in log.records[0].message
            )
            assert '3.11.5, 3.11.6, and 3.12.0' in log.records[0].message

    @override_settings(TOKEN='secret-token')
    @patch('hammett.core.bot.HammettTranslation')
    def test_run_without_python_version_warning(self, _mock_translation):
        """Test that no warning is logged for safe Python versions."""
        bot = get_bot()

        mock_version = SimpleNamespace()
        mock_version.minor = 11
        mock_version.micro = 7  # safe version

        with (
            patch('sys.version_info', mock_version),
            patch.object(bot, '_native_application', MagicMock()),
        ):
            logger = logging.getLogger('hammett.core.bot')
            with self.assertNoLogs(logger, level='WARNING'):
                bot.run()

    def test_successful_bot_initialization(self):
        """Test the case when a bot is initialized successfully."""
        bot = get_bot([TestScreenWithKeyboard])

        handlers = bot._native_application.handlers[0][0]
        pattern = calc_checksum('TestScreenWithKeyboard.move')

        assert isinstance(handlers.entry_points[0], CommandHandler)
        assert handlers.name == BOT_TEST_NAME
        # Handlers are registered in alphabetical order,
        # and the move method comes right after jump.
        assert handlers.states[DEFAULT_STATE][1].pattern == re.compile(pattern)

    def test_successful_registering_error_handler(self):
        """Test successful registering of `error_handler`."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            error_handlers=[_test_error_handler],
        )

        registered_error_handler = next(iter(bot._native_application.error_handlers))
        assert registered_error_handler == _test_error_handler

    def test_successful_registering_job(self):
        """Test successful registering of a job."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            job_configs=[
                {
                    'callback': _test_job,
                    'job_kwargs': {'trigger': 'interval'},
                },
            ],
        )
        registered_job = bot._native_application.job_queue.jobs()[0].callback
        assert registered_job == _test_job

    @override_settings(TOKEN='')
    def test_unsuccessful_bot_initialization_with_empty_token(self):
        """Test the case when a bot is initialized unsuccessfully
        because of an empty token.
        """
        with self.assertRaises(TokenIsNotSpecifiedError):
            get_bot()

    def test_unknown_handler_type_raises_exception(self):
        """Test that an unknown handler type raises UnknownHandlerTypeError exception."""
        mock_handler = MagicMock()
        mock_possible_handler = MagicMock()

        with self.assertRaises(UnknownHandlerTypeError):
            Bot._get_handler_object(
                mock_handler,
                'unknown_type',
                mock_possible_handler,
            )

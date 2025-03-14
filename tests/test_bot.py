"""The module contains the tests for the bot."""

# ruff: noqa: RUF029, S106, SLF001

import logging
import re

from telegram.ext import CommandHandler

from hammett.core.bot import Bot
from hammett.core.button import Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.exceptions import CallbackNotProvided, JobKwargsNotProvided, TokenIsNotSpecified
from hammett.core.handlers import calc_checksum
from hammett.core.mixins import RouteMixin
from hammett.core.persistence import RedisPersistence
from hammett.error_handler import default_error_handler
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import (
    BOT_TEST_NAME,
    BaseTestScreenWithDescription,
    TestScreen,
    TestStartScreen,
    get_bot,
)

_NEW_STATE = '1'

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

    routes = (
        ({DEFAULT_STATE}, _NEW_STATE),
    )


class TestScreenWithKeyboard(BaseTestScreenWithDescription):
    """The class implements the screen to test starting a bot."""

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [
            [
                Button('⬅️ Main Menu', TestStartScreen,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
        ]


class BotTests(BaseTestCase):
    """The class implements the tests for the bot."""

    @override_settings(LOGGING=_TEST_LOGGING, TOKEN='secret-token')
    def test_bot_initialization_with_logging_setup(self):
        """Test the case when a bot is initialized with
        an overriden LOGGING setting.
        """
        get_bot()
        self.assertEqual(
            logging.root.manager.loggerDict['hammett_test'].getEffectiveLevel(),
            logging.INFO,
        )

    def test_bot_initialization_with_persistence_specified(self):
        """Test a bot initialization with a persistence specified."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            persistence=RedisPersistence(),
        )

        self.assertIsNotNone(bot._native_application.persistence)
        self.assertIsInstance(bot._native_application.persistence, RedisPersistence)

    def test_bot_initialization_without_persistence_specified(self):
        """Test a bot initialization without a persistence specified."""
        bot = get_bot()
        self.assertIsNone(bot._native_application.persistence)

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
        self.assertEqual(registered_error_handlers[0], _test_error_handler)
        self.assertEqual(registered_error_handlers[1], default_error_handler)

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_TIMED_OUT': True}, TOKEN='secret-token')
    def test_registering_default_error_handler_only(self):
        """Test registering `default_error_handler` only."""
        bot = get_bot()
        registered_error_handler = next(iter(bot._native_application.error_handlers))

        self.assertEqual(registered_error_handler, default_error_handler)

    def test_registering_job_without_callback_specified(self):
        """Test registering a job without `callback` key specified."""
        with self.assertRaises(CallbackNotProvided):
            Bot(
                BOT_TEST_NAME,
                entry_point=TestStartScreen,
                job_configs=[{
                    'job_kwargs': {'trigger': 'interval'},
                }],
            )

    def test_registering_job_without_job_kwargs_specified(self):
        """Test registering a job without `job_kwargs` key specified."""
        with self.assertRaises(JobKwargsNotProvided):
            Bot(
                BOT_TEST_NAME,
                entry_point=TestStartScreen,
                job_configs=[{
                    'callback': _test_job,
                }],
            )

    def test_successful_bot_initialization(self):
        """Test the case when a bot is initialized successfully."""
        bot = get_bot([TestScreenWithKeyboard])

        handlers = bot._native_application.handlers[0][0]
        pattern = calc_checksum('TestScreenWithKeyboard.move')

        self.assertIsInstance(handlers.entry_points[0], CommandHandler)
        self.assertEqual(handlers.name, BOT_TEST_NAME)
        self.assertEqual(
            # Handlers are registered in alphabetical order,
            # and the move method comes right after jump.
            handlers.states[DEFAULT_STATE][1].pattern,
            re.compile(pattern),
        )

    def test_successful_registering_error_handler(self):
        """Test successful registering of `error_handler`."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            error_handlers=[_test_error_handler],
        )

        registered_error_handler = next(iter(bot._native_application.error_handlers))
        self.assertEqual(registered_error_handler, _test_error_handler)

    def test_successful_registering_job(self):
        """Test successful registering of a job."""
        bot = Bot(
            BOT_TEST_NAME,
            entry_point=TestStartScreen,
            job_configs=[{
                'callback': _test_job,
                'job_kwargs': {'trigger': 'interval'},
            }],
        )
        registered_job = bot._native_application.job_queue.jobs()[0].callback
        self.assertEqual(registered_job, _test_job)

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
        self.assertEqual(jump_along_route_callback, TestRouteScreen().jump_along_route)

        move_along_route_callback = bot._native_states[DEFAULT_STATE][3].callback
        self.assertEqual(move_along_route_callback, TestRouteScreen().move_along_route)

    @override_settings(TOKEN='')
    def test_unsuccessful_bot_initialization_with_empty_token(self):
        """Test the case when a bot is initialized unsuccessfully
        because of an empty token.
        """
        with self.assertRaises(TokenIsNotSpecified):
            get_bot()

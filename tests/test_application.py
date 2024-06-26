"""The module contains the tests for the application."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202, D401, S106, SLF001

import logging
import re

from telegram.ext import CommandHandler

from hammett.core import Application
from hammett.core.button import Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.exceptions import TokenIsNotSpecified
from hammett.core.handlers import calc_checksum
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import TestScreen, TestStartScreen

_APPLICATION_TEST_NAME = 'test'

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


class TestScreenWithKeyboard(TestScreen):
    """The class implements the screen to test starting an application."""

    async def add_default_keyboard(self, _update, _context):
        """Sets up the keyboard for the screen."""
        return [
            [
                Button('⬅️ Main Menu', TestStartScreen,
                       source_type=SourcesTypes.GOTO_SOURCE_TYPE),
            ],
        ]


class TestScreenWithPermissionIgnored(TestScreen):
    """The class implements the screen to test starting an application with
    a permission ignored.
    """

    async def add_default_keyboard(self, _update, _context):
        """Sets up the keyboard for the screen."""
        return [
            [
                Button(
                    '⬅️ Main Menu', TestStartScreen,
                    source_type=SourcesTypes.GOTO_SOURCE_TYPE,
                ),
            ],
        ]


class ApplicationTests(BaseTestCase):
    """The class implements the tests for the application."""

    @staticmethod
    def _init_application(screens=None) -> 'Application':
        """Returns an initialized application."""
        screens = [TestScreenWithKeyboard] if screens is None else screens

        return Application(
            _APPLICATION_TEST_NAME,
            entry_point=TestStartScreen,
            states={
                DEFAULT_STATE: screens,
            },
        )

    def test_successful_app_init(self):
        """Tests the case when an application is initialized successfully."""
        app = self._init_application()

        handlers = app._native_application.handlers[0][0]
        pattern = calc_checksum('TestScreenWithKeyboard.goto')

        self.assertIsInstance(handlers.entry_points[0], CommandHandler)
        self.assertEqual(handlers.name, _APPLICATION_TEST_NAME)
        self.assertEqual(
            handlers.states[DEFAULT_STATE][0].pattern,
            re.compile(pattern),
        )

    @override_settings(TOKEN='')
    def test_unsuccessful_app_init_with_empty_token(self):
        """Tests the case when an application is initialized unsuccessfully
        because of an empty token.
        """
        with self.assertRaises(TokenIsNotSpecified):
            self._init_application()

    @override_settings(LOGGING=_TEST_LOGGING, TOKEN='secret-token')
    def test_app_init_with_logging_setup(self):
        """Tests the case when an application is initialized with
        an overriden LOGGING setting.
        """
        self._init_application()
        self.assertEqual(
            logging.root.manager.loggerDict['hammett_test'].getEffectiveLevel(),
            logging.INFO,
        )

    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    def test_app_init_with_permissions_specified(self):
        """Tests the case when an application is initialized with
        PERMISSIONS specified.
        """
        app = self._init_application()
        handlers = app._native_application.handlers[0][0]
        is_wrapped = getattr(handlers.states[DEFAULT_STATE][0].callback, '__wrapped__', None)
        self.assertIsNotNone(is_wrapped)

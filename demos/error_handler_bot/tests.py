"""The module contains the tests for HammettErrorHandlerBot."""

# ruff: noqa: I001

import os
import unittest
from unittest.mock import AsyncMock
from telegram import Update
from telegram.ext import ApplicationHandlerStop, CallbackContext

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import (
    ERROR_HANDLING_EXAMPLES_DESCRIPTION,
    START_SCREEN_DESCRIPTION,
    ErrorHandlingExamples,
    StartScreen,
)
from error_handler import custom_error_handler
from exeptions import CustomError


class HammettErrorHandlerBotTests(BaseTestCase):
    """The class contains the tests for HammettErrorHandlerBot."""

    @catch_render_config()
    async def test_start_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await StartScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=START_SCREEN_DESCRIPTION,
            keyboard=[
                [Button(
                    '🧪 Error handling examples',
                    ErrorHandlingExamples,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                )],
                [Button(
                    '📄 Source Code',
                    'https://github.com/cusdeb-com/hammett/tree/main/demos/error_handler_bot',
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                )],
                [Button(
                    '🎸 Hammett Homepage',
                    'https://github.com/cusdeb-com/hammett',
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                )],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_error_handling_examples_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await ErrorHandlingExamples().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=ERROR_HANDLING_EXAMPLES_DESCRIPTION,
            keyboard=[
                [Button(
                    '✏️ MessageNotModified — handled by framework',
                    ErrorHandlingExamples,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE,
                )],
                [Button(
                    '⚠️ CustomError — handled by custom logic',
                    ErrorHandlingExamples().raise_custom_error,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                )],
                [Button(
                    '🔑 KeyError — unexpected',
                    ErrorHandlingExamples().raise_key_error,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                )],
                [Button(
                    '📄 Source Code',
                    'https://github.com/cusdeb-com/hammett/tree/main/demos/error_handler_bot',
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                )],
                [Button(
                    '🎸 Hammett Homepage',
                    'https://github.com/cusdeb-com/hammett',
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                )],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    async def test_raise_custom_error_handler_raises_custom_error(self):
        """Test that raise_custom_error handler raises CustomError."""
        with self.assertRaises(CustomError):
            await ErrorHandlingExamples().raise_custom_error(self.update, self.context)

    async def test_raise_key_error_handler_raises_key_error(self):
        """Test that raise_key_error handler raises KeyError."""
        with self.assertRaises(KeyError):
            await ErrorHandlingExamples().raise_key_error(self.update, self.context)

    async def test_custom_error_handler_handles_other_errors(self):
        """Test that custom_error_handler handles other errors gracefully."""
        self.context.error = ValueError('test error')

        result = await custom_error_handler(self.update, self.context)
        # Returning None passes the error to the default handler.
        # It ignores TimedOut and some BadRequest errors; everything else is re-raised.
        self.assertIsNone(result)


class CustomErrorHandlerTestsWithCallbackQuery(BaseTestCase):
    """The class implements the tests for custom_error_handler with callback_query."""

    def setUp(self):
        """Initialize a query object."""
        self._mock_query = AsyncMock()
        super().setUp()

    def get_update(self) -> 'Update':
        """Return the `Update` object with callback_query for testing purposes."""
        return Update(self.update_id, message=self.message, callback_query=self._mock_query)

    async def test_custom_error_handler_handles_custom_error_with_update(self):
        """Test that custom_error_handler handles CustomError with update."""
        self.context.error = CustomError()
        self._mock_query.answer = AsyncMock()

        with self.assertRaises(ApplicationHandlerStop):
            await custom_error_handler(self.update, self.context)

        self._mock_query.answer.assert_called_once_with('Request failed')


class CustomErrorHandlerTestsWithoutUpdate(BaseTestCase):
    """The class implements the tests for custom_error_handler without update."""

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    async def test_custom_error_handler_handles_custom_error_without_update(self):
        """Test that custom_error_handler handles CustomError without update."""
        self.context.error = CustomError()

        with self.assertRaises(ApplicationHandlerStop):
            await custom_error_handler(None, self.context)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

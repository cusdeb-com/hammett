"""The module contains the tests for the handlers."""

import logging
import zlib
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock

from telegram.ext import filters

from hammett.conf import settings
from hammett.core.constants import DEFAULT_STATE
from hammett.core.exceptions import CommandNameIsEmptyError
from hammett.core.handlers import (
    _clear_command_name,
    _get_handler_name,
    _register_handler,
    calc_checksum,
    get_payload_storage,
    log_unregistered_handler,
    register_button_handler,
    register_command_handler,
)
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase
from hammett.types.core import HandlerType
from tests.base import BaseTestScreenWithHandler

if TYPE_CHECKING:
    from hammett.types.core import Handler

_TEST_BUTTON_NAME = 'Test button'

_UNSUPPORTED_TYPE_VALUE = 1


class TestScreenWithHandler(BaseTestScreenWithHandler):
    """The class implements a screen with a handler."""


class TestScreenWithStaticHandler(Screen):
    """The class implements a screen with a static handler."""

    @staticmethod
    @register_button_handler
    async def handler(_update, _context):
        """Represent a stub handler for the testing purposes."""
        return DEFAULT_STATE


class HandlersTests(BaseTestCase):
    """The class implements the tests for the handlers."""

    def test_clearing_passed_command_name(self):
        """Test clearing a passed command name."""
        assert _clear_command_name('/test') == 'test'

    def test_create_decorator_sets_command_name(self):
        """Test that the decorator sets a cleared command name for command handlers."""
        create_decorator = _register_handler('handler_type', HandlerType.COMMAND_HANDLER)

        async def sample(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        decorated = create_decorator('/start')(sample)

        assert decorated.handler_type == HandlerType.COMMAND_HANDLER
        assert decorated.command_name == 'start'

    def test_create_decorator_sets_default_attributes(self):
        """Test that the decorator sets default attributes for a handler."""
        create_decorator = _register_handler('handler_type', HandlerType.TYPING_HANDLER)

        async def sample(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        decorated = create_decorator()(sample)

        assert decorated.handler_type == HandlerType.TYPING_HANDLER
        assert decorated.permissions_ignored == []
        assert decorated.filters is None

    def test_create_decorator_sets_filters_attribute(self):
        """Test that the decorator sets attributes for a handler."""
        create_decorator = _register_handler('handler_type', HandlerType.INPUT_HANDLER)

        async def handler(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        decorated = create_decorator(filters=filters.AUDIO)(handler)

        assert decorated.handler_type == HandlerType.INPUT_HANDLER
        assert decorated.filters is filters.AUDIO

    def test_getting_handler_name(self):
        """Test getting a handler name."""
        screen = TestScreenWithHandler()
        handler = cast('Handler', screen.handler)

        handler_name = _get_handler_name(handler)
        assert handler_name == 'TestScreenWithHandler.handler'

    def test_getting_payload_storage_when_it_is_initialized(self):
        """Test getting payload storage when it is initialized."""
        namespace = settings.PAYLOAD_NAMESPACE
        bot_data = self.context.bot_data

        existing_storage = {'foo': 'bar'}
        bot_data[namespace] = existing_storage
        storage = get_payload_storage(self.context)

        assert storage is existing_storage
        assert storage == {'foo': 'bar'}

    def test_getting_payload_storage_when_it_is_not_initialized(self):
        """Test getting payload storage when it is not initialized."""
        namespace = settings.PAYLOAD_NAMESPACE
        bot_data = self.context.bot_data
        bot_data.pop(namespace, None)
        storage = get_payload_storage(self.context)

        assert isinstance(storage, dict)
        assert namespace in bot_data
        assert storage is bot_data[namespace]
        assert storage == {}

    def test_getting_static_handler_name(self):
        """Test getting a static handler name."""
        screen = TestScreenWithStaticHandler()
        handler = cast('Handler', screen.handler)

        handler_name = _get_handler_name(handler)
        assert handler_name == 'TestScreenWithStaticHandler.handler'

    def test_log_unregistered_handler_with_non_callable(self):
        """Test log_unregistered_handler when handler is not callable."""
        logger = logging.getLogger('hammett.core.handlers')
        with self.assertNoLogs(logger, level='WARNING'):
            log_unregistered_handler(12345)

    def test_log_unregistered_handler_value_error(self):
        """Test log_unregistered_handler when ValueError is raised in try/except block."""
        logger = logging.getLogger('hammett.core.handlers')
        with self.assertNoLogs(logger, level='WARNING'):
            log_unregistered_handler(dict)

    def test_registering_command_handler_without_specified_command_name(self):
        """Test registering a command handler without specified command name."""
        with self.assertRaises(CommandNameIsEmptyError):
            class TestScreenWithCommandHandler(Screen):
                """The class implements a screen without description
                a screen for this test.
                """

                @register_command_handler('')
                async def handler(self, _update, _context):
                    """Represent a stub handler for the testing purposes."""
                    return DEFAULT_STATE

    def test_passing_string_value_to_calc_checksum(self):
        """Test passing a string value to the calc_checksum function."""
        string_value = 'test'
        string_checksum = calc_checksum(string_value)
        assert isinstance(string_checksum, str)

        expected_string_checksum = str(zlib.adler32(string_value.encode('utf8')))
        assert string_checksum == expected_string_checksum

    def test_passing_handler_to_calc_checksum(self):
        """Test passing a handler to the calc_checksum function."""
        async def handler(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        handler_name = _get_handler_name(handler)
        expected_handler_checksum = str(zlib.adler32(handler_name.encode('utf8')))
        assert calc_checksum(handler) == expected_handler_checksum

    def test_passing_unsupported_type_to_calc_checksum(self):
        """Test passing an unsupported type to the calc_checksum function."""
        with self.assertRaises(TypeError):
            calc_checksum(_UNSUPPORTED_TYPE_VALUE)

    def test_warning_about_unregistered_handler(self):
        """Test warning about an unregistered handler."""
        async def unregistered_handler(self, update, context):  # noqa: ARG001 RUF029
            return DEFAULT_STATE

        with self.assertLogs('hammett.core.handlers', level='WARNING') as log:
            log_unregistered_handler(unregistered_handler)

        assert len(log.records) == 1
        assert 'resembles a handler' in log.records[0].message
        assert unregistered_handler.__name__ in log.records[0].message

    async def test_wrapper_delegates_to_original_handler(self):
        """Test that decorated handler delegates execution to the original handler."""
        create_decorator = _register_handler('handler_type', HandlerType.BUTTON_HANDLER)
        mock_handler = AsyncMock(return_value=DEFAULT_STATE)
        decorated_handler = create_decorator()(mock_handler)

        test_args = (self, self.update, self.context)
        test_kwargs = {'extra_param': 'test_value'}

        result = await decorated_handler(*test_args, **test_kwargs)

        mock_handler.assert_called_once_with(*test_args, **test_kwargs)
        assert result == DEFAULT_STATE

"""The module contains the tests for OpenTelemetry instrumentation."""

# ruff: noqa: SLF001

import datetime
import sys
from unittest.mock import AsyncMock, MagicMock, call, patch

from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import TracerProvider
from telegram import InputMediaPhoto, Message, Update, User

from hammett.core.constants import DEFAULT_STATE, FinalRenderConfig, ParseMode, RenderConfig
from hammett.core.conversation_handler import ConversationHandler
from hammett.core.permission import Permission
from hammett.core.renderer import Renderer
from hammett.core.screen import Screen
from hammett.telemetry import HammettInstrumentor, instrument_telemetry
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import PERMISSION_DENIED_STATE, TestScreen


class TelemetryAttributesTests(BaseTestCase):
    """The class implements the tests for span attributes extraction."""

    _mock_query = AsyncMock()

    def get_message(self):
        """Return the `Message` object with text attribute for testing purposes."""
        return Message(
            self.message_id,
            datetime.datetime.now(tz=datetime.UTC),
            self.chat,
            from_user=self.user,
            text='test text',
        )

    def get_update(self):
        """Return the `Update` object for testing purposes."""
        return Update(self.update_id, message=self.message, callback_query=self._mock_query)

    def get_user(self):
        """Return the `User` object for testing purposes."""
        return User(self.user_id, 'TestUser', username='TestUsername', is_bot=False)

    def test_extracts_attributes_from_update_with_message_and_callback(self):
        """Test extracting attributes from update with message and callback query."""
        mock_span = MagicMock()

        HammettInstrumentor._add_update_attributes(mock_span, self.update, self.context)

        expected_calls = [
            call('update.id', self.update.update_id),
            call('user.id', self.user.id),
            call('user.username', self.user.username),
            call('chat.id', self.chat.id),
            call('chat.type', self.chat.type),
            call('message.id', self.message.message_id),
            call('message.text', self.message.text),
            call('callback_query.id', self.update.callback_query.id),
            call('callback_query.data', self.update.callback_query.data),
        ]
        mock_span.set_attribute.assert_has_calls(expected_calls, any_order=False)


class TelemetryTests(BaseTestCase):
    """The class implements the tests for OpenTelemetry instrumentation."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

        self.instrumentor = HammettInstrumentor()
        self.instrumentor.uninstrument()

        self.mock_tracer = MagicMock()
        self.mock_span = MagicMock()
        self.mock_tracer.start_as_current_span.return_value.__enter__ = MagicMock(
            return_value=self.mock_span,
        )
        self.mock_tracer.start_as_current_span.return_value.__exit__ = MagicMock(
            return_value=None,
        )

    async def test_conversation_handler_does_not_instrument_when_tracer_is_none(self):
        """Test that ConversationHandler.handle_update is not modified when tracer is None."""
        original_handle_update = ConversationHandler.handle_update

        self.instrumentor._instrument_conversation_handler()

        assert ConversationHandler.handle_update is original_handle_update

    async def test_conversation_handler_instruments_with_state_tracking_and_hook(self):
        """Test wrapping handle_update to create span, track state transitions, and call hook."""
        original_handle_update = AsyncMock(return_value='handled')
        ConversationHandler.handle_update = original_handle_update

        self.instrumentor.tracer = self.mock_tracer
        self.instrumentor._update_hook = MagicMock()
        self.instrumentor._instrument_conversation_handler()

        check_result = ('current-state', None, None, None)
        mock_handler_self = MagicMock()
        mock_application = MagicMock()

        with patch(
            'hammett.telemetry.instrumentor.Screen.get_current_state',
            return_value='new-state',
        ):
            result = await ConversationHandler.handle_update(
                mock_handler_self,
                self.update,
                mock_application,
                check_result,
                self.context,
            )

        assert result == 'handled'
        self.instrumentor.tracer.start_as_current_span.assert_called_once_with('telegram.update')
        self.instrumentor._update_hook.assert_called_once_with(
            self.mock_span,
            self.update,
            self.context,
        )
        original_handle_update.assert_awaited_once_with(
            mock_handler_self,
            self.update,
            mock_application,
            check_result,
            self.context,
        )
        self.mock_span.set_attribute.assert_any_call('state.current', 'current-state')
        self.mock_span.set_attribute.assert_any_call('state.new', 'new-state')

    @override_settings(OPENTELEMETRY={'ENABLED': False})
    def test_instrumentor_does_not_instrument_when_disabled(self):
        """Test that instrumentor does not instrument when ENABLED is False."""
        self.instrumentor.instrument()

        assert not self.instrumentor._instrumented
        assert self.instrumentor.tracer is None

    @override_settings(
        OPENTELEMETRY={
            'ENABLED': True,
            'SERVICE_NAME': 'test-bot',
            'EXPORTER_OTLP_ENDPOINT': 'http://localhost:4318',
        },
    )
    def test_instrumentor_initializes_opentelemetry_with_exporter(self):
        """Test initializing OpenTelemetry SDK with tracer provider and OTLP exporter."""
        self.instrumentor.instrument()

        assert self.instrumentor._instrumented
        assert self.instrumentor.tracer.resource.attributes['service.name'] == 'test-bot'
        assert isinstance(self.instrumentor.tracer._tracer_provider, TracerProvider)

        span_processor = self.instrumentor.tracer.span_processor._span_processors[0]
        assert isinstance(span_processor, BatchSpanProcessor)
        assert span_processor.span_exporter._endpoint == 'localhost:4318'

        assert self.instrumentor.tracer.instrumentation_info.name == 'hammett.instrumentation'
        assert self.instrumentor.tracer.instrumentation_info.version == '1.0.0'

    @override_settings(OPENTELEMETRY={'ENABLED': True})
    def test_instrumentor_implements_singleton_pattern(self):
        """Test that instrumentor returns the same instance for multiple instantiations."""
        instrumentor1 = HammettInstrumentor()
        instrumentor2 = HammettInstrumentor()

        assert instrumentor1 is instrumentor2

    @override_settings(
        OPENTELEMETRY={
            'ENABLED': True,
            'HANDLER_HOOK': 'tests.test_telemetry.mock_telemetry_handler_hook',
            'PERMISSION_HOOK': 'tests.test_telemetry.mock_telemetry_permission_hook',
            'UPDATE_HOOK': 'tests.test_telemetry.mock_telemetry_update_hook',
        },
    )
    def test_instrumentor_loads_custom_hooks_from_settings(self):
        """Test loading and assigning custom hook functions from settings paths."""
        self.instrumentor.instrument()

        assert self.instrumentor._handler_hook is mock_telemetry_handler_hook
        assert self.instrumentor._permission_hook is mock_telemetry_permission_hook
        assert self.instrumentor._update_hook is mock_telemetry_update_hook

    @override_settings(
        OPENTELEMETRY={
            'UPDATE_HOOK': 'tests.test_telemetry.missing_telemetry_update_hook',
            'HANDLER_HOOK': 'tests.test_telemetry.missing_telemetry_handler_hook',
        },
    )
    def test_instrumentor_silently_ignores_missing_hooks(self):
        """Test that missing hooks do not raise errors and remain as None."""
        self.instrumentor._load_hooks()

        assert self.instrumentor._update_hook is None
        assert self.instrumentor._handler_hook is None
        assert self.instrumentor._permission_hook is None

    @override_settings(OPENTELEMETRY={'ENABLED': True})
    def test_instrumentor_uninstruments_and_warns(self):
        """Test uninstrumenting the framework and logging warning about production use."""
        self.instrumentor.instrument()

        assert self.instrumentor._instrumented
        assert self.instrumentor.tracer

        with self.assertLogs('hammett.telemetry.instrumentor', level='WARNING') as logs:
            self.instrumentor.uninstrument()

        assert 'Uninstrumenting Hammett is not recommended in production' in logs.output[0]
        assert not self.instrumentor._instrumented
        assert self.instrumentor.tracer is None

    @override_settings(OPENTELEMETRY={'ENABLED': True})
    def test_instrumentor_warns_when_instrumenting_twice(self):
        """Test logging warning when attempting to instrument already instrumented framework."""
        self.instrumentor.instrument()

        with self.assertLogs('hammett.telemetry.instrumentor', level='WARNING') as logs:
            self.instrumentor.instrument()

        assert 'already instrumented' in logs.output[0]

    @override_settings(OPENTELEMETRY={'ENABLED': True})
    def test_instrumentor_warns_when_opentelemetry_not_installed(self):
        """Test logging error when OpenTelemetry packages are not installed."""
        with (
            patch.dict(sys.modules, {'opentelemetry': None}),
            self.assertLogs('hammett.telemetry.instrumentor', level='WARNING') as logs,
        ):
            self.instrumentor.instrument()

        assert 'not installed' in logs.output[0]

    async def test_permission_calls_denied_handler_when_sync_check_fails(self):
        """Test calling handle_permission_denied when synchronous has_permission returns False."""

        class TestPermission(Permission):
            def has_permission(self, _update, _context):
                return False

            async def handle_permission_denied(self, _update, _context):
                return PERMISSION_DENIED_STATE

        self.instrumentor.tracer = self.mock_tracer

        permission = TestPermission()
        original_handler = AsyncMock()

        self.instrumentor._instrument_permissions()
        wrapped_handler = permission.check_permission(original_handler)
        result = await wrapped_handler(MagicMock(), self.update, self.context)

        assert result == PERMISSION_DENIED_STATE
        original_handler.assert_not_awaited()
        self.mock_span.set_attribute.assert_any_call('permission.granted', False)  # noqa: FBT003

    async def test_permission_calls_handler_and_hook_when_async_check_succeeds(self):
        """Test calling original handler and custom hook when async has_permission returns True."""

        class TestPermission(Permission):
            async def has_permission(self, _update, _context):
                return True

            async def handle_permission_denied(self, _update, _context):
                return DEFAULT_STATE

        permission = TestPermission()
        original_handler = AsyncMock(return_value='handled')
        self.instrumentor._permission_hook = MagicMock()
        self.instrumentor.tracer = self.mock_tracer
        self.instrumentor._instrument_permissions()
        wrapped_handler = permission.check_permission(original_handler)

        screen_self = MagicMock()
        result = await wrapped_handler(screen_self, self.update, self.context)

        assert result == 'handled'
        original_handler.assert_awaited_once_with(screen_self, self.update, self.context)
        self.instrumentor._permission_hook.assert_called_once_with(self.mock_span, permission, True)  # noqa: FBT003
        self.mock_span.set_attribute.assert_any_call('permission.granted', True)  # noqa: FBT003

    async def test_permission_does_not_instrument_when_tracer_is_none(self):
        """Test that Permission.check_permission is not modified when tracer is None."""
        original_check_permission = Permission.check_permission

        self.instrumentor._instrument_permissions()

        assert Permission.check_permission is original_check_permission

    async def test_renderer_adds_attributes_to_span(self):
        """Test creating span with renderer attributes for cover, document, and attachments."""
        original_render = AsyncMock(return_value='message')
        Renderer.render = original_render

        self.instrumentor.tracer = self.mock_tracer
        self.instrumentor._instrument_screen_rendering()
        config = FinalRenderConfig(
            cover='cover',
            document={'media': b'doc', 'document_kwargs': {}},
            attachments=[InputMediaPhoto('https://example.com/image.png')],
            cache_covers=True,
        )

        renderer = Renderer(ParseMode.HTML)
        result = await renderer.render(self.update, self.context, config)

        assert result == 'message'
        self.mock_tracer.start_as_current_span.assert_any_call(
            'renderer.render',
            attributes={
                'renderer.has_cover': True,
                'renderer.has_document': True,
                'renderer.has_attachments': True,
                'renderer.cache_covers': True,
            },
        )
        original_render.assert_awaited_once_with(renderer, self.update, self.context, config)

    async def test_screen_adds_attributes_to_span(self):
        """Test creating span with screen name and render mode attributes."""
        original_render = AsyncMock()
        Screen.render = original_render

        self.instrumentor.tracer = self.mock_tracer
        self.instrumentor._instrument_screen_rendering()
        config = RenderConfig(as_new_message=True)

        mock_screen = TestScreen()
        await mock_screen.render(self.update, self.context, config=config)

        self.mock_tracer.start_as_current_span.assert_any_call(
            'screen.render',
            attributes={
                'screen.name': 'TestScreen',
                'screen.as_new_message': True,
            },
        )
        original_render.assert_awaited_once_with(
            mock_screen,
            self.update,
            self.context,
            config=config,
        )

    async def test_screen_does_not_instrument_when_tracer_is_none(self):
        """Test that Screen.render and Renderer.render are not modified when tracer is None."""
        original_render = Screen.render
        original_renderer_render = Screen.renderer_class.render

        self.instrumentor._instrument_screen_rendering()

        assert Screen.render is original_render
        assert Screen.renderer_class.render is original_renderer_render

    def test_setup_function_calls_instrumentor_when_enabled(self):
        """Test calling HammettInstrumentor.instrument() when ENABLED is True."""
        with patch.object(HammettInstrumentor, 'instrument') as instrument_mock:
            instrument_telemetry({'ENABLED': True})

        instrument_mock.assert_called_once_with()

    def test_setup_function_returns_early_when_disabled(self):
        """Test that HammettInstrumentor.instrument() is not called when ENABLED is False."""
        with patch.object(HammettInstrumentor, 'instrument') as instrument_mock:
            instrument_telemetry({'ENABLED': False})

        instrument_mock.assert_not_called()


def mock_telemetry_handler_hook(span, _handler, _screen):
    """Mock telemetry handler hook for testing."""
    span.set_attribute('custom.attribute', 'test_handler_hook_value')


def mock_telemetry_permission_hook(span, _permission, _granted):
    """Mock telemetry permission hook for testing."""
    span.set_attribute('custom.attribute', 'test_permission_hook_value')


def mock_telemetry_update_hook(span, _update, _context):
    """Mock telemetry update hook for testing."""
    span.set_attribute('custom.attribute', 'test_update_hook_value')

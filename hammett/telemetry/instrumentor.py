"""The module contains automatic instrumentation of framework components
for distributed tracing with OpenTelemetry.
"""

import asyncio
import contextlib
import logging
from functools import wraps
from typing import TYPE_CHECKING, cast

from hammett.conf import settings
from hammett.core.screen import Screen
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from typing import Any, Self

    from opentelemetry.trace import Span, Tracer
    from telegram import Message, Update
    from telegram.ext import Application, CallbackContext
    from telegram.ext._utils.types import BD, BT, CCT, CD, UD

    from hammett.core.constants import FinalRenderConfig, RenderConfig
    from hammett.core.permission import Permission
    from hammett.types.core import CheckUpdateType, Handler
    from hammett.types.telemetry import (
        TelemetryHandlerHook,
        TelemetryPermissionHook,
        TelemetryUpdateHook,
    )

LOGGER = logging.getLogger(__name__)


class HammettInstrumentor:
    """The class represents automatic instrumentation of key components
    including conversation handlers, screen rendering, and permission checks.
    """

    _instance: 'HammettInstrumentor | None' = None
    _instrumented = False

    def __new__(  # noqa: PYI034
        cls: type['HammettInstrumentor'],
        *args: 'Any',
        **kwargs: 'Any',
    ) -> 'HammettInstrumentor':
        """Implement singleton pattern.

        Returns:
            Instance of HammettInstrumentor.

        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self: 'Self') -> None:
        """Initialize the instrumentor."""
        self.tracer: Tracer | None = None
        self._update_hook: TelemetryUpdateHook | None = None
        self._handler_hook: TelemetryHandlerHook | None = None
        self._permission_hook: TelemetryPermissionHook | None = None

    def instrument(self: 'Self') -> None:
        """Instrument the framework."""
        if self._instrumented:
            LOGGER.warning('Hammett is already instrumented with OpenTelemetry')
            return

        if not settings.OPENTELEMETRY.get('ENABLED', False):
            LOGGER.info('OpenTelemetry is disabled in settings')
            return

        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import SERVICE_NAME, Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
        except ImportError:
            LOGGER.exception(
                'OpenTelemetry packages are not installed. '
                'Install them with: pip install opentelemetry-api opentelemetry-sdk '
                'opentelemetry-exporter-otlp-proto-grpc',
            )
            return

        service_name = settings.OPENTELEMETRY.get('SERVICE_NAME', 'hammett')
        resource = Resource(attributes={SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)

        if endpoint := settings.OPENTELEMETRY.get('EXPORTER_OTLP_ENDPOINT'):
            otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)

        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer('hammett.instrumentation', '1.0.0')

        self._load_hooks()

        self._instrument_conversation_handler()
        self._instrument_screen_rendering()
        self._instrument_permissions()

        self._instrumented = True
        LOGGER.info('Hammett instrumented with OpenTelemetry successfully')

    def _load_hooks(self: 'Self') -> None:
        """Load custom hooks from the configuration."""
        config = settings.OPENTELEMETRY
        if update_hook_path := config.get('UPDATE_HOOK'):
            with contextlib.suppress(ImportError):
                self._update_hook = import_string(update_hook_path)

        if handler_hook_path := config.get('HANDLER_HOOK'):
            with contextlib.suppress(ImportError):
                self._handler_hook = import_string(handler_hook_path)

        if permission_hook_path := config.get('PERMISSION_HOOK'):
            with contextlib.suppress(ImportError):
                self._permission_hook = import_string(permission_hook_path)

    def _instrument_conversation_handler(self: 'Self') -> None:
        """Instrument ConversationHandler to trace update processing."""
        tracer = self.tracer
        if tracer is None:
            return

        from hammett.core.conversation_handler import ConversationHandler

        original_handle_update = ConversationHandler.handle_update

        @wraps(original_handle_update)
        async def traced_handle_update(
            handler_self: 'ConversationHandler',
            update: 'Update',
            application: 'Application[Any, CCT, Any, Any, Any, Any]',
            check_result: 'CheckUpdateType[CCT]',
            context: 'CCT',
        ) -> object | None:
            with tracer.start_as_current_span('telegram.update') as span:
                self._add_update_attributes(span, update, context)

                if self._update_hook:
                    with contextlib.suppress(Exception):
                        self._update_hook(span, update, context)

                current_state, _, _, _ = check_result
                span.set_attribute('state.current', str(current_state))

                result = await original_handle_update(
                    handler_self,
                    update,
                    application,
                    check_result,
                    context,
                )

                if hasattr(context, 'user_data') and context.user_data is not None:
                    new_state = Screen.get_current_state(context)
                    if new_state is not None:
                        span.set_attribute('state.new', str(new_state))

                return result

        ConversationHandler.handle_update = traced_handle_update  # type: ignore[assignment, method-assign]

    def _instrument_screen_rendering(self: 'Self') -> None:
        """Instrument Screen.render to trace screen rendering operations."""
        tracer = self.tracer
        if tracer is None:
            return

        from hammett.core.screen import Screen

        original_render = Screen.render

        @wraps(original_render)
        async def traced_render(
            screen_self: 'Screen',
            update: 'Update | None',
            context: 'CallbackContext[BT, UD, CD, BD]',
            *,
            config: 'RenderConfig | None' = None,
            **kwargs: 'Any',
        ) -> None:
            with tracer.start_as_current_span(
                'screen.render',
                attributes={
                    'screen.name': screen_self.__class__.__name__,
                    'screen.as_new_message': getattr(config, 'as_new_message', False),
                },
            ):
                await original_render(screen_self, update, context, config=config, **kwargs)

        Screen.render = traced_render  # type: ignore[assignment, method-assign]

        original_renderer_render = Screen.renderer_class.render

        @wraps(original_renderer_render)
        async def traced_renderer_render(
            renderer_self: 'Renderer',
            update: 'Update | None',
            context: 'CallbackContext[BT, UD, CD, BD]',
            config: 'FinalRenderConfig',
            **kwargs: 'Any',
        ) -> 'Message | tuple[Message] | None':
            with tracer.start_as_current_span(
                'renderer.render',
                attributes={
                    'renderer.has_cover': bool(config.cover),
                    'renderer.has_document': bool(config.document),
                    'renderer.has_attachments': bool(config.attachments),
                    'renderer.cache_covers': config.cache_covers,
                },
            ):
                return await original_renderer_render(
                    renderer_self,
                    update,
                    context,
                    config,
                    **kwargs,
                )

        from hammett.core.renderer import Renderer

        Renderer.render = traced_renderer_render  # type: ignore[assignment, method-assign]

    def _instrument_permissions(self: 'Self') -> None:
        """Instrument permission checks to trace access control."""
        tracer = self.tracer
        if tracer is None:
            return

        from hammett.core.permission import Permission

        original_check_permission = Permission.check_permission
        permission_hook = self._permission_hook

        def traced_check_permission(
            permission_self: 'Permission',
            handler: 'Handler',
        ) -> 'Handler':
            wrapped_handler = original_check_permission(permission_self, handler)

            @wraps(wrapped_handler)
            async def wrapper(
                screen: 'Screen',
                update: 'Update',
                context: 'CallbackContext[BT, UD, CD, BD]',
                *args: 'Any',
                **kwargs: 'Any',
            ) -> 'Any':
                with tracer.start_as_current_span(
                    'permission.check',
                    attributes={'permission.name': permission_self.__class__.__name__},
                ) as span:
                    if asyncio.iscoroutinefunction(permission_self.has_permission):
                        permitted = await permission_self.has_permission(update, context)  # type: ignore[arg-type]
                    else:
                        permitted = permission_self.has_permission(update, context)

                    span.set_attribute('permission.granted', permitted)

                    if permission_hook:
                        with contextlib.suppress(Exception):
                            permission_hook(span, permission_self, permitted)

                    if permitted:
                        return await handler(screen, update, context, *args, **kwargs)  # type: ignore[arg-type]

                    return await permission_self.handle_permission_denied(update, context)

            return cast('Handler', wrapper)

        Permission.check_permission = traced_check_permission  # type: ignore[assignment, method-assign]

    @staticmethod
    def _add_update_attributes(
        span: 'Span',
        update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Add common attributes from Telegram update to span."""
        span.set_attribute('update.id', update.update_id)

        if user := update.effective_user:
            span.set_attribute('user.id', user.id)
            if user.username:
                span.set_attribute('user.username', user.username)

        if chat := update.effective_chat:
            span.set_attribute('chat.id', chat.id)
            span.set_attribute('chat.type', chat.type)

        if message := update.message:
            span.set_attribute('message.id', message.message_id)
            if text := message.text:
                span.set_attribute('message.text', text)

        if callback_query := update.callback_query:
            span.set_attribute('callback_query.id', update.callback_query.id)
            if callback_query_data := callback_query.data:
                span.set_attribute('callback_query.data', callback_query_data)

    def uninstrument(self: 'Self') -> None:
        """Uninstrument the framework."""
        if not self._instrumented:
            return

        LOGGER.warning('Uninstrumenting Hammett is not recommended in production')
        self._instrumented = False
        self.tracer = None


def instrument_telemetry(telemetry_settings: 'dict[str, Any]') -> None:
    """Initialize OpenTelemetry instrumentation if enabled in settings."""
    if not telemetry_settings.get('ENABLED'):
        return

    HammettInstrumentor().instrument()

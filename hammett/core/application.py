"""The module contains the implementation of the high-level application class."""

from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import Application as NativeApplication
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from hammett.core.conversation_handler import ConversationHandler
from hammett.core.exceptions import (
    CallbackForJobHasNotBeenProvided,
    JobKwargsHaveNotBeenProvided,
    TokenIsNotSpecified,
    UnknownHandlerType,
)
from hammett.core.handlers import calc_checksum, log_unregistered_handler
from hammett.core.permission import apply_permission_to
from hammett.types import HandlerAlias, HandlerType, JobConfig
from hammett.utils.log import configure_logging

if TYPE_CHECKING:
    from collections.abc import Iterable

    from telegram.ext import BasePersistence
    from telegram.ext._applicationbuilder import ApplicationBuilder
    from telegram.ext._utils.types import BD, CD, UD
    from typing_extensions import Self

    from hammett.core.mixins import StartMixin
    from hammett.core.screen import Screen
    from hammett.types import Handler, NativeStates, State, States

__all__ = ('Application', )


class Application:
    """The class is a wrapper for the native Application class.
    The wrapping solves the following tasks:
    - hiding low-level technical details of python-telegram-bot from developers;
    - registering handlers;
    - configuring logging.
    """

    def __init__(  # noqa: PLR0913
        self: 'Self',
        name: str,
        *,
        entry_point: 'type[StartMixin]',
        error_handlers: 'list[Handler] | None' = None,
        job_configs: 'list[JobConfig] | None' = None,
        native_states: 'NativeStates | None' = None,
        persistence: 'BasePersistence[UD, CD, BD] | None' = None,
        states: 'States | None' = None,
    ) -> None:
        """Initialize an application object."""
        from hammett.conf import settings

        if not settings.TOKEN:
            raise TokenIsNotSpecified

        self._setup()

        self._route_handlers = ('sjump', 'smove')
        self._builtin_handlers = ('jump', 'move', 'start', *self._route_handlers)
        self._entry_point = entry_point()
        self._name = name
        self._native_states = native_states or {}
        self._states = states

        builder = self.provide_application_builder()
        if persistence:
            builder.persistence(persistence)

        self._native_application = builder.build()

        if self._states:
            for state in self._states.items():
                self._register_handlers(*state)

        self._register_error_handlers(error_handlers)
        self._register_jobs(job_configs)

        start_handler = apply_permission_to(self._entry_point.start)
        self._native_application.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start', start_handler)],
            states=self._native_states,
            fallbacks=[CommandHandler('start', start_handler)],
            name=self._name,
            persistent=bool(persistence),
        ))

    @staticmethod
    def _get_handler_object(
        handler: 'HandlerAlias',
        handler_type: 'Any | str | None',
        possible_handler: 'Handler',
    ) -> CallbackQueryHandler[Any] | MessageHandler[Any]:
        """Return the handler object depending on its type."""
        handler_object: CallbackQueryHandler[Any] | MessageHandler[Any]
        if handler_type in {HandlerType.BUTTON_HANDLER, ''}:
            handler_object = CallbackQueryHandler(
                apply_permission_to(handler),
                # Specify a pattern. The pattern is used to determine which handler
                # should be triggered when a specific button is pressed.
                pattern=calc_checksum(handler),
            )
        elif handler_type == HandlerType.COMMAND_HANDLER:
            handler_object = MessageHandler(
                filters.COMMAND & filters.Regex(f'^/{possible_handler.command_name}'),
                handler,
            )
        elif handler_type == HandlerType.INPUT_HANDLER:
            handler_object = MessageHandler(
                possible_handler.filters,  # type: ignore[arg-type]
                handler,
            )
        elif handler_type == HandlerType.TYPING_HANDLER:
            handler_object = MessageHandler(
                filters.TEXT & (~filters.COMMAND),
                handler,
            )
        else:
            raise UnknownHandlerType

        return handler_object

    def _register_error_handlers(
        self: 'Self',
        error_handlers: 'list[Handler] | None',
    ) -> None:
        """Register the specified error handlers."""
        if error_handlers:
            for error_handler in error_handlers:
                self._native_application.add_error_handler(error_handler)  # type: ignore[arg-type]

    def _register_jobs(
        self: 'Self',
        job_configs: 'list[JobConfig] | None' = None,
    ) -> None:
        """Register the specified job queue handlers."""
        if job_configs:
            job_queue = self._native_application.job_queue
            for i, job_config in enumerate(job_configs):
                callback = job_config.get('callback')
                if callback is None:
                    msg = (
                        f'You must provide the callback function that will be executed by the job '
                        f'in configuration with index {i}'
                    )
                    raise CallbackForJobHasNotBeenProvided(msg)

                job_kwargs = job_config.get('job_kwargs')
                if not job_kwargs:
                    msg = (
                        f'You must provide the keyword arguments (job_kwargs) for the '
                        f'configuration of the job with index {i}'
                    )
                    raise JobKwargsHaveNotBeenProvided(msg)

                if job_queue:
                    job_queue.run_custom(**job_config)

    def _register_handlers(self: 'Self', state: 'State', screens: 'Iterable[type[Screen]]') -> None:
        self._set_default_value_to_native_states(state)

        for screen in screens:
            instance = screen()
            for name in dir(instance):
                acceptable_handler_types = (
                    HandlerType.BUTTON_HANDLER,
                    HandlerType.COMMAND_HANDLER,
                    HandlerType.INPUT_HANDLER,
                    HandlerType.TYPING_HANDLER,
                )
                handler, handler_type = None, None
                possible_handler = getattr(instance, name)
                possible_handler_type = getattr(possible_handler, 'handler_type', '')
                if (
                    name in self._builtin_handlers or
                    possible_handler_type in acceptable_handler_types
                ):
                    handler, handler_type = possible_handler, possible_handler_type

                if handler is None:
                    log_unregistered_handler(possible_handler)
                    continue

                handler_object = self._get_handler_object(handler, handler_type, possible_handler)

                if (
                    hasattr(instance, 'routes')
                    and name in self._route_handlers
                    and instance.routes
                ):
                    for route in instance.routes:
                        route_states, _ = route
                        for route_state in route_states:
                            self._set_default_value_to_native_states(route_state)
                            self._native_states[route_state].append(handler_object)
                else:
                    self._native_states[state].append(handler_object)

    def _set_default_value_to_native_states(self: 'Self', state: 'State') -> None:
        """Set default value to native states."""
        try:
            self._native_states[state]
        except KeyError:
            self._native_states[state] = []

    def _setup(self: 'Self') -> None:
        """Configure logging."""
        from hammett.conf import settings
        configure_logging(settings.LOGGING)

    def provide_application_builder(self: 'Self') -> 'ApplicationBuilder':  # type: ignore[type-arg]
        """Return a native application builder."""
        from hammett.conf import settings

        return NativeApplication.builder().token(settings.TOKEN)

    def run(self: 'Self') -> None:
        """Run the application."""
        from hammett.conf import settings

        if settings.USE_WEBHOOK:
            self._native_application.run_webhook(
                listen=settings.WEBHOOK_LISTEN,
                port=settings.WEBHOOK_PORT,
                url_path=settings.WEBHOOK_URL_PATH,
                webhook_url=settings.WEBHOOK_URL,
                allowed_updates=Update.ALL_TYPES,
            )
        else:
            self._native_application.run_polling(allowed_updates=Update.ALL_TYPES)

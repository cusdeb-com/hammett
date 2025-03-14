"""The module contains the implementation of the high-level Bot class."""

# ruff: noqa: PLR2004

import logging
import sys
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
    CallbackNotProvided,
    JobKwargsNotProvided,
    TokenIsNotSpecified,
    UnknownHandlerType,
)
from hammett.core.handlers import calc_checksum, log_unregistered_handler
from hammett.core.permission import apply_permission_to
from hammett.error_handler import default_error_handler
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
    from hammett.types import Handler, HandlerAlias, NativeStates, State, States

__all__ = ('Bot', )

logger = logging.getLogger(__name__)


class Bot:
    """The class is a wrapper for the native Application class.
    The wrapping solves the following tasks:
    - hiding low-level technical details of python-telegram-bot from developers;
    - registering handlers;
    - configuring logging.
    """

    def __init__(
        self: 'Self',
        name: str,
        *,
        entry_point: 'type[StartMixin]',
        error_handlers: 'list[HandlerAlias] | None' = None,
        job_configs: 'list[JobConfig] | None' = None,
        native_states: 'NativeStates | None' = None,
        persistence: 'BasePersistence[UD, CD, BD] | None' = None,
        states: 'States | None' = None,
    ) -> None:
        """Initialize a bot object.

        Raises
        ------
            TokenIsNotSpecified: If the `TOKEN` attribute in the settings is not specified.

        """
        from hammett.conf import settings

        if not settings.TOKEN:
            raise TokenIsNotSpecified

        self._setup()

        self._route_handlers = ('jump_along_route', 'move_along_route')
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

        self._native_application.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start', self._entry_point.start)],
            states=self._native_states,
            fallbacks=[CommandHandler('start', self._entry_point.start)],
            name=self._name,
            persistent=bool(persistence),
        ))

    @staticmethod
    def _get_handler_object(
        handler: 'HandlerAlias',
        handler_type: 'Any | str | None',
        possible_handler: 'Handler',
    ) -> CallbackQueryHandler[Any, Any] | MessageHandler[Any, Any]:
        """Return the handler object depending on its type.

        Returns
        -------
            Handler object.

        Raises
        ------
            UnknownHandlerType: If the handler type is unknown.

        """
        handler_object: CallbackQueryHandler[Any, Any] | MessageHandler[Any, Any]
        if handler_type in {HandlerType.BUTTON_HANDLER, ''}:
            handler_object = CallbackQueryHandler(
                handler,
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
                possible_handler.filters,
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
        error_handlers: 'list[HandlerAlias] | None',
    ) -> None:
        """Register the specified error handlers."""
        from hammett.conf import settings

        if any(settings.ERROR_HANDLER_CONF.values()):
            if error_handlers:
                error_handlers.append(default_error_handler)
            else:
                error_handlers = [default_error_handler]

        if error_handlers:
            for error_handler in error_handlers:
                self._native_application.add_error_handler(error_handler)

    def _register_jobs(
        self: 'Self',
        job_configs: 'list[JobConfig] | None' = None,
    ) -> None:
        """Register the specified job queue handlers.

        Raises
        ------
            CallbackNotProvided: If `callback` of `JobConfig` is not provided.
            JobKwargsNotProvided: If `job_kwargs` of `JobConfig` is not provided.

        """
        if job_configs is not None:
            job_queue = self._native_application.job_queue
            for i, job_config in enumerate(job_configs):
                callback = job_config.get('callback')
                if callback is None:
                    msg = (
                        f'You must provide a callback function that will be executed by the job '
                        f'under the index {i}'
                    )
                    raise CallbackNotProvided(msg)

                job_kwargs = job_config.get('job_kwargs')
                if not job_kwargs:
                    msg = f'You must provide job_kwargs for the job under the index {i}'
                    raise JobKwargsNotProvided(msg)

                if job_queue:
                    job_queue.run_custom(**job_config)

    def _register_handlers(self: 'Self', state: 'State', screens: 'Iterable[type[Screen]]') -> None:
        self._set_default_value_to_native_states(state)

        for screen in screens:
            for name in dir(screen):
                acceptable_handler_types = (
                    HandlerType.BUTTON_HANDLER,
                    HandlerType.COMMAND_HANDLER,
                    HandlerType.INPUT_HANDLER,
                    HandlerType.TYPING_HANDLER,
                )
                handler, handler_type = None, None
                possible_handler = getattr(screen, name)
                possible_handler_type = getattr(possible_handler, 'handler_type', '')
                if (
                    name in self._builtin_handlers or
                    possible_handler_type in acceptable_handler_types
                ):
                    handler, handler_type = possible_handler, possible_handler_type

                if handler is None:
                    log_unregistered_handler(possible_handler)
                    continue

                setattr(screen, name, apply_permission_to(handler))
                instance_handler = getattr(screen(), name)
                handler_object = self._get_handler_object(
                    instance_handler,
                    handler_type,
                    possible_handler,
                )

                if (
                    hasattr(screen, 'routes')
                    and name in self._route_handlers
                    and screen.routes
                ):
                    for route in screen.routes:
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
        """Return a native application builder.

        Returns
        -------
            Native application builder.

        """
        from hammett.conf import settings

        return NativeApplication.builder().read_timeout(
            settings.APPLICATION_BUILDER_READ_TIMEOUT,
        ).token(
            settings.TOKEN,
        )

    def run(self: 'Self') -> None:
        """Run the bot."""
        from hammett.conf import settings

        if ((
            sys.version_info.minor == 11 and (
            sys.version_info.micro == 5 or sys.version_info.micro == 6
        )) or (
            sys.version_info.minor == 12 and sys.version_info.micro == 0
        )):
            logger.warning(
                "It's recommended to avoid using the following versions of Python: "
                "3.11.5, 3.11.6, and 3.12.0. The reason for this recommendation is that "
                "these versions raise a `RuntimeError` upon bot termination, which may "
                "lead to an improper shutdown process.",
            )

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

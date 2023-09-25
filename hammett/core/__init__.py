"""The core of the Hammett framework."""

from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import Application as NativeApplication
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from hammett.core.exceptions import TokenIsNotSpecified, UnknownHandlerType
from hammett.core.handlers import calc_checksum, log_unregistered_handler
from hammett.core.permissions import apply_permission_to
from hammett.core.screen import ConversationHandler, Screen
from hammett.types import HandlerType
from hammett.utils.log import configure_logging

if TYPE_CHECKING:
    from collections.abc import Iterable

    from telegram.ext import BasePersistence
    from telegram.ext._utils.types import BD, CD, UD
    from typing_extensions import Self

    from hammett.core.screen import StartScreen
    from hammett.types import NativeStates, States

__all__ = ('Application', )


class Application:
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
        entry_point: 'type[StartScreen]',
        native_states: 'NativeStates | None' = None,
        persistence: 'BasePersistence[UD, CD, BD] | None' = None,
        states: 'States | None' = None,
    ) -> None:
        from hammett.conf import settings

        if not settings.TOKEN:
            raise TokenIsNotSpecified

        self._setup()

        self._builtin_handlers = ('goto', 'start')
        self._entry_point = entry_point()
        self._name = name
        self._native_states = native_states or {}
        self._states = states

        builder = NativeApplication.builder().token(settings.TOKEN)
        if persistence:
            builder.persistence(persistence)

        self._native_application = builder.build()

        if self._states:
            for state in self._states.items():
                self._register_handlers(*state)

        start_handler = apply_permission_to(self._entry_point.start)
        self._native_application.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start', start_handler)],
            states=self._native_states,
            fallbacks=[CommandHandler('start', start_handler)],
            name=self._name,
            persistent=bool(persistence),
        ))

    def _register_handlers(self: 'Self', state: int, screens: 'Iterable[type[Screen]]') -> None:
        try:
            self._native_states[state]
        except KeyError:
            self._native_states[state] = []

        for screen in screens:
            instance = screen()
            for name in dir(instance):
                acceptable_handler_types = (
                    HandlerType.button_handler,
                    HandlerType.typing_handler,
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

                handler_object: CallbackQueryHandler[Any] | MessageHandler[Any]
                if handler_type in (HandlerType.button_handler, ''):
                    handler_object = CallbackQueryHandler(
                        apply_permission_to(handler),
                        # Specify a pattern. The pattern is used to determine which handler
                        # should be triggered when a specific button is pressed.
                        pattern=calc_checksum(handler),
                    )
                elif handler_type == HandlerType.typing_handler:
                    handler_object = MessageHandler(
                        filters.TEXT & (~filters.COMMAND),
                        handler,
                    )
                else:
                    raise UnknownHandlerType

                self._native_states[state].append(handler_object)

    def _setup(self: 'Self') -> None:
        """Configures logging."""

        from hammett.conf import settings
        configure_logging(settings.LOGGING)

    def run(self: 'Self') -> None:
        """Runs the application."""

        self._native_application.run_polling(allowed_updates=Update.ALL_TYPES)

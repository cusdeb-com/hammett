"""The core of the Hammett framework."""

from typing import TYPE_CHECKING, cast

from telegram import Update
from telegram.ext import Application as NativeApplication
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
)

from hammett.core.exceptions import TokenIsNotSpecified, UnknownHandlerType
from hammett.core.handlers import calc_checksum, log_unregistered_handler
from hammett.core.screen import ConversationHandler, Screen
from hammett.types import HandlerType
from hammett.utils.log import configure_logging
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Iterable

    from telegram.ext import BasePersistence
    from telegram.ext._utils.types import BD, CD, UD
    from typing_extensions import Self

    from hammett.core.permissions import Permission
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

        self._native_application.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start', self._entry_point.start)],
            states=self._native_states,
            fallbacks=[CommandHandler('start', self._entry_point.start)],
            name=self._name,
            persistent=bool(persistence),
        ))

    def _register_handlers(self: 'Self', state: int, screens: 'Iterable[type[Screen]]') -> None:
        from hammett.conf import settings

        try:
            self._native_states[state]
        except KeyError:
            self._native_states[state] = []

        for screen in screens:
            instance = screen()
            for name in dir(instance):
                handler, handler_type = None, None
                possible_handler = getattr(instance, name)
                if (
                    name in self._builtin_handlers or
                    getattr(possible_handler, 'handler_type', '') == HandlerType.button_handler
                ):
                    handler, handler_type = possible_handler, HandlerType.button_handler

                if handler is None:
                    log_unregistered_handler(possible_handler)
                    continue

                handler_wrapped = None
                for permission_path in settings.PERMISSIONS:
                    permission: type['Permission'] = import_string(permission_path)
                    permissions_ignored = getattr(handler, 'permissions_ignored', None)
                    if permissions_ignored and permission.CLASS_UUID in permissions_ignored:
                        continue

                    permission_instance = permission()
                    handler_wrapped = permission_instance.check_permission(handler)

                if handler_type == HandlerType.button_handler:
                    handler_object = CallbackQueryHandler(
                        handler_wrapped or handler,
                        # Specify a pattern. The pattern is used to determine which handler
                        # should be triggered when a specific button is pressed.
                        pattern=calc_checksum(handler),
                    )
                    self._native_states[state].append(handler_object)
                else:
                    raise UnknownHandlerType

    def _setup(self: 'Self') -> None:
        """Configures logging."""

        from hammett.conf import settings
        configure_logging(settings.LOGGING)

    def run(self: 'Self') -> None:
        """Runs the application."""

        self._native_application.run_polling(allowed_updates=Update.ALL_TYPES)

from typing import TYPE_CHECKING, cast

from telegram import Update
from telegram.ext import Application as NativeApplication
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
)

from hammett.core.constants import SourcesTypes
from hammett.core.exceptions import TokenIsNotSpecified
from hammett.core.screen import Button, ConversationHandler
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from telegram.ext import BasePersistence
    from telegram.ext._utils.types import BD, CD, UD
    from typing_extensions import Self

    from hammett.core.permissions import Permission
    from hammett.core.screen import Screen
    from hammett.types import Handler, NativeStates, Stage, States


class Application:
    def __init__(
        self: 'Self',
        name: str,
        *,
        entry_point: 'type[Screen]',
        native_states: 'NativeStates | None' = None,
        persistence: 'BasePersistence[UD, CD, BD] | None' = None,
        states: 'States | None' = None,
    ) -> None:
        from hammett.conf import settings

        if not settings.TOKEN:
            raise TokenIsNotSpecified

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

    def _register_handlers(self: 'Self', state: int, screens: list[type['Screen']]) -> None:
        from hammett.conf import settings

        self._native_states[state] = []
        for screen in screens:
            obj = screen()
            for buttons_row in obj.setup_keyboard():
                for button in buttons_row:
                    if button.source_type not in (SourcesTypes.GOTO_SOURCE_TYPE,
                                                  SourcesTypes.HANDLER_SOURCE_TYPE):
                        continue

                    if button.source_type == SourcesTypes.GOTO_SOURCE_TYPE:
                        source = cast('Handler[..., Stage]', button.source_goto)
                    else:
                        source = cast('Handler[..., Stage]', button.source)

                    for permission_path in settings.PERMISSIONS:
                        permission: type['Permission'] = import_string(permission_path)
                        permissions_ignored = getattr(button.source, 'permissions_ignored', None)
                        if permissions_ignored and permission.CLASS_UUID in permissions_ignored:
                            continue

                        permission_instance = permission()
                        button.source_wrapped = permission_instance.check_permission(
                            source,  # type: ignore[assignment]
                        )

                    self._native_states[state].append(CallbackQueryHandler(
                        button.source_wrapped or source,  # type: ignore[arg-type]
                        pattern=f'^{Button.create_handler_pattern(source)}$',
                    ))

    def run(self: 'Self') -> None:
        """Runs the application. """

        self._native_application.run_polling(allowed_updates=Update.ALL_TYPES)

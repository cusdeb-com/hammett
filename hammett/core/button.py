"""The module contains the implementation of the button component that is used in the keyboard."""

from typing import TYPE_CHECKING, cast

from telegram import InlineKeyboardButton

from hammett.core import handlers
from hammett.core.constants import SourcesTypes
from hammett.core.exceptions import ImproperlyConfigured, UnknownSourceType
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.hiders import Hider, HidersChecker
    from hammett.types import Handler, Source

_HANDLER_SOURCES_TYPES = (
    SourcesTypes.GOTO_SOURCE_TYPE,
    SourcesTypes.HANDLER_SOURCE_TYPE,
    SourcesTypes.JUMP_SOURCE_TYPE,
    SourcesTypes.SGOTO_SOURCE_TYPE,
    SourcesTypes.SJUMP_SOURCE_TYPE,
)

_SHORTCUT_SOURCES_TYPES = (
    SourcesTypes.GOTO_SOURCE_TYPE,
    SourcesTypes.JUMP_SOURCE_TYPE,
    SourcesTypes.SGOTO_SOURCE_TYPE,
    SourcesTypes.SJUMP_SOURCE_TYPE,
)


class Button:
    """The class implements the interface of a button."""

    hiders_checker: 'HidersChecker | None' = None

    def __init__(
        self: 'Self',
        caption: str,
        source: 'Source',
        *,
        source_type: 'SourcesTypes' = SourcesTypes.HANDLER_SOURCE_TYPE,
        hiders: 'Hider | None' = None,
        payload: str | None = None,
    ) -> None:
        """Initialize a button object."""
        self.caption = caption
        self.payload = payload
        self.source = source
        self.source_type = source_type
        self.hiders = hiders

        self._check_source()
        self._init_hider_checker()

    #
    # Private methods
    #

    def _check_source(self: 'Self') -> None:
        """Check if the source is valid. If it's invalid, the method raises `TypeError`."""
        from hammett.core.screen import Screen

        if self.source_type in _SHORTCUT_SOURCES_TYPES:
            screen = cast('type[Screen]', self.source)
            if issubclass(screen, Screen):
                if self.source_type == SourcesTypes.GOTO_SOURCE_TYPE:
                    self.source_shortcut = cast('Handler', screen().goto)
                elif self.source_type == SourcesTypes.JUMP_SOURCE_TYPE:
                    self.source_shortcut = cast('Handler', screen().jump)
                elif self.source_type == SourcesTypes.SGOTO_SOURCE_TYPE:
                    self.source_shortcut = cast(
                        'Handler', screen().sgoto,  # type: ignore[attr-defined]
                    )
                else:
                    self.source_shortcut = cast(
                        'Handler', screen().sjump,   # type: ignore[attr-defined]
                    )
            else:
                msg = (
                    f'The source "{self.source}" must be a subclass of Screen if its '
                    f'source_type is either SourcesTypes.GOTO_SOURCE_TYPE or '
                    f'SourcesTypes.JUMP_SOURCE_TYPE'
                )
                raise TypeError(msg)

        if self.source_type == SourcesTypes.HANDLER_SOURCE_TYPE and not callable(self.source):
            msg = (
                f'The source "{self.source}" must be callable if its '
                f'source_type is SourcesTypes.HANDLER_SOURCE_TYPE'
            )
            raise TypeError(msg)

    @staticmethod
    def _get_user_id(
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> int | None:
        """Obtain the user ID from either an Update object or a CallbackContext object."""
        if update is None:
            return context._user_id  # noqa: SLF001

        return update.effective_user.id  # type: ignore[union-attr]

    def _init_hider_checker(self: 'Self') -> None:
        if self.hiders and not self.hiders_checker:
            from hammett.conf import settings

            if not settings.HIDERS_CHECKER:
                msg = "The 'HIDERS_CHECKER' setting is not set"
                raise ImproperlyConfigured(msg)

            if self.hiders:
                hiders_checker: type[HidersChecker] = import_string(settings.HIDERS_CHECKER)
                self.hiders_checker = hiders_checker(self.hiders.hiders_set)

    async def _specify_visibility(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        visibility = True
        if (
            self.hiders and
            self.hiders_checker and
            not await self.hiders_checker.run(update, context)
        ):
            visibility = False

        return visibility

    #
    # Public methods
    #

    async def create(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> tuple[InlineKeyboardButton, bool]:
        """Create the button."""
        visibility = await self._specify_visibility(update, context)

        if self.source_type in _HANDLER_SOURCES_TYPES:
            if self.source_type in _SHORTCUT_SOURCES_TYPES and self.source_shortcut:
                source = self.source_shortcut
            else:
                source = cast('Handler', self.source)

            data = (
                f'{handlers.calc_checksum(source)},'
                f'button={handlers.calc_checksum(self.caption)},'
                f'user_id={self._get_user_id(update, context)}'
            )

            if self.payload is not None:
                payload_storage = handlers.get_payload_storage(context)
                payload_storage[data] = self.payload

            return InlineKeyboardButton(self.caption, callback_data=data), visibility

        if self.source_type == SourcesTypes.URL_SOURCE_TYPE and isinstance(self.source, str):
            return InlineKeyboardButton(self.caption, url=self.source), visibility

        raise UnknownSourceType

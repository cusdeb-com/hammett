"""The module contains the implementation of the button component that is used in the keyboard."""

from typing import TYPE_CHECKING, cast

from telegram import InlineKeyboardButton, WebAppInfo

from hammett.core import handlers
from hammett.core.constants import SourceTypes
from hammett.core.exceptions import ImproperlyConfigured, UnknownSourceType
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.hider import Hider, HidersChecker
    from hammett.types import Handler, Source

_HANDLER_SOURCES_TYPES = (
    SourceTypes.HANDLER_SOURCE_TYPE,
    SourceTypes.JUMP_ALONG_ROUTE_SOURCE_TYPE,
    SourceTypes.JUMP_SOURCE_TYPE,
    SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
    SourceTypes.MOVE_SOURCE_TYPE,
)

_SHORTCUT_SOURCES_TYPES = (
    SourceTypes.JUMP_ALONG_ROUTE_SOURCE_TYPE,
    SourceTypes.JUMP_SOURCE_TYPE,
    SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
    SourceTypes.MOVE_SOURCE_TYPE,
)


class Button:
    """The class implements the interface of a button."""

    hiders_checker: 'HidersChecker | None' = None

    def __init__(
        self: 'Self',
        caption: str,
        source: 'Source',
        *,
        source_type: 'SourceTypes' = SourceTypes.HANDLER_SOURCE_TYPE,
        hiders: 'Hider | None' = None,
        payload: str | None = None,
        chat_id: int | None = None,
    ) -> None:
        """Initialize a button object."""
        self.caption = caption
        self.chat_id = chat_id
        self.payload = payload
        self.source = source
        self.source_type = source_type
        self.hiders = hiders

        self._check_source()
        self._init_hider_checker()

    #
    # Private methods
    #

    def __eq__(self, other: object) -> bool:
        """Compare two Button objects.

        Returns
        -------
            Result of comparing two Button objects.

        """
        if not isinstance(other, Button):
            return super().__eq__(other)

        return (
            self.caption == other.caption and
            self.source == other.source and
            self.source_type == other.source_type and
            self.hiders == other.hiders and
            self.payload == other.payload and
            self.chat_id == other.chat_id
        )

    def __hash__(self) -> int:
        """Return the object hash.

        Returns
        -------
            Object hash.

        """
        return hash((
            self.caption, self.source, self.source_type, self.hiders, self.payload, self.chat_id,
        ))

    def _check_source(self: 'Self') -> None:
        """Check if the source is valid.

        Raises
        ------
            TypeError: If the source of the button is invalid.

        """
        from hammett.core.screen import Screen

        if self.source_type in _SHORTCUT_SOURCES_TYPES:
            screen = cast('type[Screen]', self.source)
            if issubclass(screen, Screen):
                if self.source_type == SourceTypes.JUMP_SOURCE_TYPE:
                    self.source_shortcut = cast('Handler', screen().jump)
                elif self.source_type == SourceTypes.MOVE_SOURCE_TYPE:
                    self.source_shortcut = cast('Handler', screen().move)
                elif self.source_type == SourceTypes.JUMP_ALONG_ROUTE_SOURCE_TYPE:
                    self.source_shortcut = cast(
                        'Handler', screen().jump_along_route,   # type: ignore[attr-defined]
                    )
                else:
                    self.source_shortcut = cast(
                        'Handler', screen().move_along_route,  # type: ignore[attr-defined]
                    )
            else:
                msg = (
                    f'The source "{self.source}" must be a subclass of Screen if its '
                    f'source_type is either SourceTypes.MOVE_SOURCE_TYPE or '
                    f'SourceTypes.JUMP_SOURCE_TYPE'
                )
                raise TypeError(msg)

        if self.source_type == SourceTypes.HANDLER_SOURCE_TYPE and not callable(self.source):
            msg = (
                f'The source "{self.source}" must be callable if its '
                f'source_type is SourceTypes.HANDLER_SOURCE_TYPE'
            )
            raise TypeError(msg)

    @staticmethod
    def _get_user_id(
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> int | None:
        """Obtain the user ID from either an Update object or a CallbackContext object.

        Returns
        -------
            ID of the user.

        """
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
        """Create the button.

        Returns
        -------
            Object of the `InlineKeyboardButton` type.

        Raises
        ------
            UnknownSourceType: If the source type of the button is unknown.

        """
        visibility = await self._specify_visibility(update, context)

        if self.source_type in _HANDLER_SOURCES_TYPES:
            if self.source_type in _SHORTCUT_SOURCES_TYPES and self.source_shortcut:
                source = self.source_shortcut
            else:
                source = cast('Handler', self.source)

            chat_id = self._get_user_id(update, context) or self.chat_id
            data = (
                f'{handlers.calc_checksum(source)},'
                f'button={handlers.calc_checksum(self.caption)},'
                f'user_id={chat_id}'
            )

            if self.payload is not None:
                payload_storage = handlers.get_payload_storage(context)
                payload_storage[data] = self.payload

            return InlineKeyboardButton(self.caption, callback_data=data), visibility

        if self.source_type == SourceTypes.URL_SOURCE_TYPE and isinstance(self.source, str):
            return InlineKeyboardButton(self.caption, url=self.source), visibility

        if self.source_type == SourceTypes.WEB_APP_SOURCE_TYPE and isinstance(self.source, str):
            return InlineKeyboardButton(
                self.caption,
                web_app=WebAppInfo(url=self.source),
            ), visibility

        raise UnknownSourceType

import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ConversationHandler as NativeConversationHandler

from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.core.exceptions import (
    ImproperlyConfigured,
    UnknownSourceType,
)
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from os import PathLike
    from typing import Any

    from telegram import CallbackQuery, Update
    from telegram.ext import Application, CallbackContext
    from telegram.ext._utils.types import BD, BT, CCT, CD, UD
    from typing_extensions import Self

    from hammett.core.hiders import Hider, HidersChecker
    from hammett.types import CheckUpdateType, Handler, Keyboard, Source, Stage


class Button:
    hiders_checker: 'HidersChecker | None' = None

    def __init__(
        self: 'Self',
        caption: str,
        source: 'Source',
        *,
        source_type: SourcesTypes = SourcesTypes.HANDLER_SOURCE_TYPE,
        hiders: 'Hider | None' = None,
    ) -> None:
        self.caption = caption
        self.source = source
        self.source_wrapped = None
        self.source_type = source_type
        self.hiders = hiders

        self.source_goto = None
        if source_type == SourcesTypes.GOTO_SOURCE_TYPE:
            if not callable(source) or not isinstance(source, type(Screen)):
                msg = (
                    f'The source "{source}" must be callable if its '
                    f'source_type is SourcesTypes.GOTO_SOURCE_TYPE'
                )
                raise TypeError(msg)

            screen = source()
            self.source_goto = cast('Handler[..., Stage]', screen.goto)

        if self.hiders and not self.hiders_checker:
            self._init_hider_checker()

    #
    # Private methods
    #

    def _init_hider_checker(self: 'Self') -> None:
        from hammett.conf import settings

        if not settings.HIDERS_CHECKER:
            msg = "The 'HIDERS_CHECKER' setting is not set"
            raise ImproperlyConfigured(msg)

        if self.hiders:
            hiders_checker: type['HidersChecker'] = import_string(settings.HIDERS_CHECKER)
            self.hiders_checker = hiders_checker(self.hiders.hiders_set)

    async def _specify_visibility(
        self: 'Self',
        update: 'Update',
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

    @staticmethod
    def create_handler_pattern(handler: 'Handler[..., Stage]') -> str:
        return f'{type(handler.__self__).__name__}.{handler.__name__}'

    async def create(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> tuple[InlineKeyboardButton, bool]:
        visibility = await self._specify_visibility(update, context)

        if self.source_type in (SourcesTypes.GOTO_SOURCE_TYPE, SourcesTypes.HANDLER_SOURCE_TYPE):
            if self.source_type == SourcesTypes.GOTO_SOURCE_TYPE and self.source_goto:
                source = self.source_goto
            else:
                source = cast('Handler[..., Stage]', self.source)

            pattern = self.create_handler_pattern(source)
            return InlineKeyboardButton(self.caption, callback_data=pattern), visibility

        if self.source_type == SourcesTypes.URL_SOURCE_TYPE and isinstance(self.source, str):
            return InlineKeyboardButton(self.caption, url=self.source), visibility

        raise UnknownSourceType


class ConversationHandler(NativeConversationHandler['Any']):
    async def handle_update(  # type: ignore[override]
        self: 'Self',
        update: 'Update',
        application: 'Application[Any, CCT, Any, Any, Any, Any]',
        check_result: 'CheckUpdateType[CCT]',
        context: 'CCT',
    ) -> object | None:
        try:
            res = await super().handle_update(update, application, check_result, context)
        except BadRequest as exc:  # noqa: TRY302
            raise exc  # noqa: TRY201
        else:
            return res


@dataclass
class RenderConfig:
    """The class that represents a config for the Screen render method. """

    as_new_message: bool = False
    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    keyboard: 'Keyboard | None' = None


class Screen:
    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    html_parse_mode: 'ParseMode | DefaultValue[None]' = DEFAULT_NONE

    _instance: 'Screen | None' = None

    def __init__(self: 'Self') -> None:
        if self.html_parse_mode is DEFAULT_NONE:
            from hammett.conf import settings
            self.html_parse_mode = settings.HTML_PARSE_MODE

    def __new__(cls: type['Screen'], *args: tuple['Any'], **kwargs: dict[str, 'Any']) -> 'Screen':
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    #
    # Private methods
    #

    @staticmethod
    async def _create_markup_keyboard(
        rows: list[list['Button']],
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> InlineKeyboardMarkup:
        keyboard = []
        for row in rows:
            buttons = []
            for button in row:
                inline_button, visible = await button.create(update, context)
                if visible:
                    buttons.append(inline_button)

            keyboard.append(buttons)

        return InlineKeyboardMarkup(keyboard)

    async def _get_edit_render_method(
        self: 'Self',
        update: 'Update',
        *,
        cache_covers: bool = False,
        cover: 'str | PathLike[str]' = '',
        description: str = '',
    ) -> tuple['Callable[..., Awaitable[Any]] | None', dict[str, 'Any']]:
        """Returns the render method and its kwargs for editing a message. """

        kwargs: dict[str, 'Any'] = {}
        send: 'Callable[..., Awaitable[Any]] | None' = None

        query = await self.get_callback_query(update)
        if query:
            if cover:
                if self._is_url(cover):
                    kwargs['media'] = InputMediaPhoto(
                        caption=description,
                        media=str(cover) if cache_covers else f'{cover}?{uuid4()}',
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    with Path(cover).open('rb') as infile:
                        kwargs['media'] = InputMediaPhoto(
                            caption=description,
                            media=infile,
                            parse_mode=ParseMode.HTML,
                        )
                send = query.edit_message_media
            else:
                kwargs['parse_mode'] = ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE
                kwargs['text'] = description
                send = query.edit_message_text

        return send, kwargs

    async def _get_new_message_render_method(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        cache_covers: bool = False,
        cover: 'str | PathLike[str]' = '',
        description: str = '',
    ) -> tuple['Callable[..., Awaitable[Any]]', dict[str, 'Any']]:
        """Returns the render method and its kwargs for sending a new message. """

        kwargs: dict[str, 'Any'] = {
            'parse_mode': ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        }

        if update.effective_chat:
            chat_id = update.effective_chat.id
            kwargs['chat_id'] = chat_id

        if cover:
            if self._is_url(cover) and cache_covers:
                cover = f'{cover}?{uuid4()}'

            kwargs['caption'] = description
            kwargs['photo'] = cover

            send = context.bot.send_photo
        else:
            kwargs['text'] = description

            send = context.bot.send_message

        return send, kwargs

    @staticmethod
    def _is_url(cover: 'str | PathLike[str]') -> bool:
        """Checks if the cover is specified using either a local path or a URL. """

        return bool(re.search(r'^https?://', str(cover)))

    #
    # Public methods
    #

    @staticmethod
    async def get_callback_query(update: 'Update') -> 'CallbackQuery | None':
        """Gets CallbackQuery from Update. """

        query = update.callback_query
        # CallbackQueries need to be answered, even if no notification to the user is needed.
        # Some clients may have trouble otherwise.
        # See https://core.telegram.org/bots/api#callbackquery
        if query:
            await query.answer()

        return query

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Switches to the screen. """

        await self.render(update, context)
        return DEFAULT_STAGE

    async def render(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
    ) -> None:
        """Renders the screen components (i.e., cover, description and keyboard). """

        config = config or RenderConfig()
        cache_covers = config.cache_covers or self.cache_covers
        cover = config.cover or self.cover
        description = config.description or self.description
        keyboard = config.keyboard or self.setup_keyboard()

        send: 'Callable[..., Awaitable[Any]] | None' = None
        if config.as_new_message:
            send, kwargs = await self._get_new_message_render_method(
                update,
                context,
                cache_covers=cache_covers,
                cover=cover,
                description=description,
            )
        else:
            send, kwargs = await self._get_edit_render_method(
                update,
                cache_covers=cache_covers,
                cover=cover,
                description=description,
            )

        if send:
            await send(
                reply_markup=await self._create_markup_keyboard(keyboard, update, context),
                **kwargs,
            )

    def setup_keyboard(self: 'Self') -> 'Keyboard':
        """Sets up the keyboard for the screen. """

        return []

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        raise NotImplementedError

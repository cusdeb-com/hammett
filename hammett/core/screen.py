"""The module contains the implementation of the screen components
(i.e., cover, description and keyboard).
"""

import logging
import re
from dataclasses import asdict
from os import PathLike
from typing import TYPE_CHECKING, cast
from uuid import uuid4

import aiofiles
from telegram import (
    InlineKeyboardMarkup,
    InputMediaDocument,
    InputMediaPhoto,
    Message,
)
from telegram._files.photosize import PhotoSize
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram.constants import ParseMode

from hammett.core import handlers
from hammett.core.constants import DEFAULT_STATE, EMPTY_KEYBOARD, FinalRenderConfig, RenderConfig
from hammett.core.exceptions import (
    FailedToGetDataAttributeOfQuery,
    PayloadIsEmpty,
    ScreenDescriptionIsEmpty,
    ScreenDocumentDataIsEmpty,
    ScreenRouteIsEmpty,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from telegram import CallbackQuery, Update
    from telegram._utils.types import FileInput
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Attachments, Document, Keyboard, Routes, State

LOGGER = logging.getLogger(__name__)


class Screen:
    """The class implements the interface of a screen."""

    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    document: 'Document | None' = None
    html_parse_mode: 'ParseMode | DefaultValue[None]' = DEFAULT_NONE
    routes: 'Routes | None' = None

    _cached_covers: dict[str | PathLike[str], str] = {}
    _initialized: bool = False
    _instance: 'Screen | None' = None

    def __init__(self: 'Self') -> None:
        if not self._initialized:
            if self.html_parse_mode is DEFAULT_NONE:
                from hammett.conf import settings
                self.html_parse_mode = settings.HTML_PARSE_MODE

            self._initialized = True

    def __new__(cls: type['Screen'], *args: 'Any', **kwargs: 'Any') -> 'Screen':
        """Implements the singleton pattern."""

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    #
    # Private methods
    #

    def _create_input_media_document(
        self: 'Self',
        document: 'Document',
        caption: str = '',
    ) -> InputMediaDocument:
        """Creates an object that represents a document to be sent."""

        data = document.get('data')
        if not data:
            msg = f'The document data of {self.__class__.__name__} is empty'
            raise ScreenDocumentDataIsEmpty(msg)

        return InputMediaDocument(
            caption=caption,
            filename=document.get('name', ''),
            media=data,
            parse_mode=ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        )

    def _create_input_media_photo(
        self: 'Self',
        caption: str,
        media: 'FileInput | PhotoSize',
    ) -> InputMediaPhoto:
        """Creates an object that represents a photo to be sent."""

        return InputMediaPhoto(
            caption=caption,
            media=media,
            parse_mode=ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        )

    @staticmethod
    async def _create_markup_keyboard(
        rows: 'Keyboard',
        update: 'Update | None',
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
        cover: 'str | PathLike[str] | PhotoSize' = '',
        description: str = '',
        document: 'Document | None' = None,
    ) -> tuple['Callable[..., Awaitable[Any]] | None', dict[str, 'Any']]:
        """Returns the render method and its kwargs for editing a message."""

        kwargs: 'Any' = {}
        send: 'Callable[..., Awaitable[Any]] | None' = None

        query = await self.get_callback_query(update)
        if query:
            if document or cover:
                media = document or cover
                kwargs = await self._get_edit_render_method_media_kwargs(
                    cache_covers=cache_covers,
                    description=description,
                    media=media,
                )

                send = query.edit_message_media
            else:
                kwargs['parse_mode'] = ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE
                kwargs['text'] = description
                send = query.edit_message_text

        return send, kwargs

    async def _get_edit_render_method_media_kwargs(
        self: 'Self',
        media: 'Document | str | PathLike[str] | PhotoSize',
        *,
        description: str = '',
        cache_covers: bool = False,
    ) -> 'Any':
        """Returns the kwargs for edit render method with media."""

        kwargs: 'Any' = {}
        if isinstance(media, dict):
            kwargs['media'] = self._create_input_media_document(
                media,
                caption=description,
            )
        elif isinstance(media, PhotoSize):
            kwargs['media'] = self._create_input_media_photo(
                caption=description,
                media=media,
            )
        elif self._is_url(media):
            kwargs['media'] = self._create_input_media_photo(
                caption=description,
                media=str(media) if cache_covers else f'{media}?{uuid4()}',
            )
        elif media in self._cached_covers:
            kwargs['media'] = self._create_input_media_photo(
                caption=description,
                media=self._cached_covers[media],
            )
        else:
            async with aiofiles.open(media, 'rb') as infile:
                file = await infile.read()
                kwargs['media'] = self._create_input_media_photo(
                    caption=description,
                    media=file,
                )

        return kwargs

    async def _get_new_message_render_method(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        cache_covers: bool = False,
        chat_id: int = 0,
        cover: 'str | PathLike[str]' = '',
        description: str = '',
        document: 'Document | None' = None,
        attachments: 'Attachments | None' = None,
    ) -> tuple['Callable[..., Awaitable[Any]]', dict[str, 'Any']]:
        """Returns the render method and its kwargs for sending a new message."""

        kwargs: 'Any' = {
            'chat_id': chat_id or context._chat_id,  # noqa: SLF001
            'parse_mode': ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        }

        if cover:
            if self._is_url(cover) and cache_covers:
                cover = f'{cover}?{uuid4()}'
            elif cache_covers:
                cover_file_id = self._cached_covers.get(cover)
                cover = cover_file_id if cover_file_id else cover

            kwargs['caption'] = description
            kwargs['photo'] = cover

            send = context.bot.send_photo
        elif document:
            kwargs['document'] = self._create_input_media_document(document=document).media
            kwargs['caption'] = description

            send = context.bot.send_document
        elif attachments:
            kwargs['media'] = attachments

            send = context.bot.send_media_group
        else:
            kwargs['text'] = description

            send = context.bot.send_message

        return send, kwargs

    @staticmethod
    def _is_url(cover: 'str | PathLike[str]') -> bool:
        """Checks if the cover is specified using either a local path or a URL."""

        return bool(re.search(r'^https?://', str(cover)))

    async def _finalize_config(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None',
    ) -> 'FinalRenderConfig':
        """Finalizes an object of RenderConfig returning an object of FinalRenderConfig."""

        final_config = FinalRenderConfig(**asdict(config)) if config else FinalRenderConfig()
        final_config.cache_covers = (
            final_config.cache_covers or await self.get_cache_covers(update, context)
        )
        final_config.cover = final_config.cover or await self.get_cover(update, context)

        final_config.description = (
            final_config.description or await self.get_description(update, context)
        )
        final_config.document = final_config.document or await self.get_document(update, context)
        if (
            not final_config.description and not final_config.document and
            not final_config.attachments
        ):
            msg = f'The description of {self.__class__.__name__} is empty'
            raise ScreenDescriptionIsEmpty(msg)

        if not config or config.keyboard is None:
            final_config.keyboard = final_config.keyboard or self.setup_keyboard()

        return final_config

    async def _pre_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
        extra_data: 'Any | None',
    ) -> 'Message | None':
        """Runs before screen rendering."""

    async def _render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
        _extra_data: 'Any | None',
    ) -> 'Message | None':
        """Renders the screen components (i.e., cover, description and keyboard),
        and returns a corresponding object of the Message type.
        """

        send: 'Callable[..., Awaitable[Any]] | None' = None
        kwargs: 'Any' = {}
        if config.as_new_message:
            send, kwargs = await self._get_new_message_render_method(
                context,
                cache_covers=config.cache_covers,
                chat_id=config.chat_id,
                cover=config.cover,
                description=config.description,
                document=config.document,
                attachments=config.attachments,
            )
        elif update:
            send, kwargs = await self._get_edit_render_method(
                update,
                cache_covers=config.cache_covers,
                cover=config.cover,
                description=config.description,
                document=config.document,
            )

        message: 'Message | None' = None
        if send and kwargs:
            # Unfortunately, it's currently not possible to send a keyboard along
            # with a group of attachments
            if not config.attachments:
                kwargs['reply_markup'] = await self._create_markup_keyboard(
                    config.keyboard,
                    update,
                    context,
                )

            send_object = await send(**kwargs)

            message = send_object
            if config.cover and config.cache_covers and not self._is_url(config.cover):
                photo_size_object = send_object.photo[-1]
                self._cached_covers[config.cover] = photo_size_object.file_id

        return message

    async def _post_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        message: 'Message',
        config: 'FinalRenderConfig',
        extra_data: 'Any | None',
    ) -> None:
        """Runs after screen rendering."""

    #
    # Public methods
    #

    @staticmethod
    async def get_callback_query(update: 'Update') -> 'CallbackQuery | None':
        """Gets CallbackQuery from Update."""

        query = update.callback_query
        # CallbackQueries need to be answered, even if no notification to the user is needed.
        # Some clients may have trouble otherwise.
        # See https://core.telegram.org/bots/api#callbackquery
        if query:
            await query.answer()

        return query

    async def get_cache_covers(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Returns the `cache_covers` attribute of the screen."""

        return self.cache_covers

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'RenderConfig':
        """Returns the Screen's config."""

        return RenderConfig()

    async def get_cover(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'str | PathLike[str]':
        """Returns the `cover` attribute of the screen."""

        return self.cover

    async def get_current_state(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Returns the current state."""

        return cast('State', context.user_data.get('current_state'))  # type: ignore[union-attr]

    async def get_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Returns the `description` attribute of the screen."""

        return self.description

    async def get_document(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Document | None':
        """Returns the `document` attribute of the screen."""

        return self.document

    async def get_payload(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Returns the payload passed through the pressed button."""

        query = await self.get_callback_query(update)
        data = getattr(query, 'data', None)
        if data is None:
            raise FailedToGetDataAttributeOfQuery

        try:
            payload_storage = handlers.get_payload_storage(context)
            return payload_storage.pop(data)
        except KeyError as exc:
            raise PayloadIsEmpty from exc

    async def render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> None:
        """Renders the screen components (i.e., cover, description and keyboard)."""

        final_config = await self._finalize_config(update, context, config)
        await self._pre_render(update, context, final_config, extra_data)

        message = await self._render(update, context, final_config, extra_data)
        if message:
            await self._post_render(update, context, message, final_config, extra_data)

    def setup_keyboard(self: 'Self') -> 'Keyboard':
        """Sets up the keyboard for the screen."""

        return EMPTY_KEYBOARD

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switches to the screen re-rendering the previous message."""

        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switches to the screen sending it as a new message."""

        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> 'State':
        """Sends the screen to the specified chat."""

        config = config or RenderConfig()
        config.as_new_message = True

        await self.render(None, context, config=config, extra_data=extra_data)
        return DEFAULT_STATE


class RouteMixin(Screen):
    """Mixin to switch between screens which are registered
    in different states.
    """

    def __init__(self: 'Self') -> None:
        super().__init__()

        if self.routes is None:
            msg = f'The route of {self.__class__.__name__} is empty'
            raise ScreenRouteIsEmpty(msg)

    async def _get_return_state_from_routes(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        routes: 'Routes',
    ) -> 'State':
        """Returns the first found state in the routes."""

        current_state = await self.get_current_state(update, context)

        for route in routes:
            route_states, return_state = route
            if current_state in route_states:
                return return_state

        return current_state

    async def sgoto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Changes the state and switches to the screen re-rendering
        the previous message.
        """

        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return await self._get_return_state_from_routes(
            update, context, self.routes,  # type: ignore[arg-type]
        )

    async def sjump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Changes the state and switches to the screen sending
        it as a new message.
        """

        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return await self._get_return_state_from_routes(
            update, context, self.routes,  # type: ignore[arg-type]
        )


class StartScreen(Screen):
    """The base class for start screens (i.e, the screens
    that show up on the /start command).
    """

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoked on the /start command."""

        return await self.jump(update, context)

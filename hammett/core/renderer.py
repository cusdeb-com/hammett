"""The module contains the implementation of the screen rendering."""

import re
from typing import TYPE_CHECKING
from uuid import uuid4

import aiofiles
from telegram import InlineKeyboardMarkup, InputMediaDocument, InputMediaPhoto, PhotoSize
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.constants import ParseMode

from hammett.core.exceptions import ScreenDocumentDataIsEmpty
from hammett.utils.misc import get_callback_query

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from os import PathLike
    from typing import Any

    from telegram import Message, Update
    from telegram._utils.types import FileInput
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.constants import FinalRenderConfig
    from hammett.types import Attachments, Document, Keyboard


class Renderer:
    """The class implements screen rendering."""

    _cached_covers: 'dict[str | PathLike[str], str]' = {}

    def __init__(self: 'Self', html_parse_mode: 'ParseMode') -> None:
        self.html_parse_mode = html_parse_mode

    #
    # Private methods
    #

    @staticmethod
    def _is_url(cover: 'str | PathLike[str]') -> bool:
        """Checks if the cover is specified using either a local path or a URL."""

        return bool(re.search(r'^https?://', str(cover)))

    def _create_input_media_document(
        self: 'Self',
        document: 'Document',
        caption: str = '',
    ) -> 'InputMediaDocument':
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
    ) -> 'InputMediaPhoto':
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
    ) -> 'InlineKeyboardMarkup':
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

        query = await get_callback_query(update)
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

    #
    # Public methods
    #

    async def render(
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

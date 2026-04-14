"""The module contains the implementation of the screen rendering."""

import contextlib
import re
from os import PathLike
from typing import TYPE_CHECKING, ClassVar
from uuid import uuid4

import aiofiles
from telegram import InlineKeyboardMarkup, InputMediaDocument, InputMediaPhoto, PhotoSize, error
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.error import BadRequest

from hammett.core.constants import EMPTY_KEYBOARD, FinalRenderConfig
from hammett.core.exceptions import ScreenDocumentDataIsEmptyError, ScreenRenderNotSupportedError

_NO_MESSAGE_TO_EDIT = 'There is no text in the message to edit'

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any, Self

    from telegram import Message, Update
    from telegram._utils.types import FileInput
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.core.constants import LatestMessage, ParseMode
    from hammett.types.core import Document, Keyboard


class Renderer:
    """The class implements screen rendering."""

    # Class-level cache shared by all Renderer instances and
    # reduce memory usage.
    _cached_covers: ClassVar[dict[str | PathLike[str], str]] = {}

    def __init__(self: 'Self', parse_mode: 'ParseMode | None') -> None:
        """Initialize a renderer object."""
        self.parse_mode = DEFAULT_NONE if parse_mode is None else parse_mode.value

    #
    # Private methods
    #

    def _create_input_media_document(
        self: 'Self',
        document: 'Document',
        description: str,
    ) -> InputMediaDocument:
        """Create an object that represents a document to be sent.

        Returns:
            Object of the `InputMediaDocument` type with passed attributes.

        Raises:
            ScreenDocumentDataIsEmptyError: If the `media` attribute of the `Document`
            type object is empty.

        """
        try:
            media = document['media']
        except KeyError as exc:
            msg = f'The document data of {self.__class__.__name__} is empty'
            raise ScreenDocumentDataIsEmptyError(msg) from exc

        document_kwargs = document.get('document_kwargs', {})
        if not document_kwargs.get('caption'):
            document_kwargs['caption'] = description

        document_kwargs['parse_mode'] = self.parse_mode

        return InputMediaDocument(media, **document_kwargs)

    def _create_input_media_photo(
        self: 'Self',
        caption: str,
        media: 'FileInput | PhotoSize',
    ) -> InputMediaPhoto:
        """Create an object that represents a photo to be sent.

        Returns:
            Object of the `InputMediaPhoto` type with passed attributes.

        """
        return InputMediaPhoto(caption=caption, media=media, parse_mode=self.parse_mode)

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
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
    ) -> tuple['Callable[..., Awaitable[Any]] | None', dict[str, 'Any']]:
        """Return the render method and its kwargs for editing a message.

        Returns:
            Render method and its kwargs for editing a message.

        """
        kwargs: Any = {
            'chat_id': config.chat_id,
            'message_id': config.message_id,
        }

        send: Callable[..., Awaitable[Any]] | None = None
        if config.document or config.cover:
            media = config.document or config.cover
            media_kwargs = await self._get_edit_render_method_media_kwargs(
                cache_covers=config.cache_covers,
                description=config.description,
                media=media,
            )
            kwargs.update(media_kwargs)

            send = context.bot.edit_message_media
        else:
            kwargs['parse_mode'] = self.parse_mode
            kwargs['text'] = config.description

            send = context.bot.edit_message_text

        return send, kwargs

    async def _get_edit_render_method_media_kwargs(
        self: 'Self',
        media: 'Document | str | PathLike[str] | PhotoSize',
        *,
        description: str = '',
        cache_covers: bool = False,
    ) -> 'Any':
        """Return the kwargs for edit render method with media.

        Returns:
            Kwargs for edit render method with media.

        """
        kwargs: Any = {}
        if isinstance(media, dict):
            kwargs['media'] = self._create_input_media_document(media, description)
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
        config: 'FinalRenderConfig',
    ) -> tuple['Callable[..., Awaitable[Any]]', dict[str, 'Any']]:
        """Return the render method and its kwargs for sending a new message.

        Returns:
            Render method and its kwargs for sending a new message.

        """
        kwargs: Any = {
            'chat_id': config.chat_id,
            'parse_mode': self.parse_mode,
        }

        cover = config.cover
        send: Callable[..., Awaitable[Any]]
        if config.document:
            input_media_document = self._create_input_media_document(
                config.document,
                config.description,
            )
            kwargs['caption'] = input_media_document.caption
            kwargs['document'] = input_media_document.media

            send = context.bot.send_document
        elif cover:
            if self._is_url(cover) and config.cache_covers:
                cover = f'{cover}?{uuid4()}'
            elif config.cache_covers:
                cover_file_id = self._cached_covers.get(cover)
                cover = cover_file_id or cover

            kwargs['caption'] = config.description
            kwargs['photo'] = cover

            send = context.bot.send_photo
        elif config.attachments:
            kwargs['media'] = config.attachments

            send = context.bot.send_media_group
        else:
            kwargs['text'] = config.description

            send = context.bot.send_message

        return send, kwargs

    @staticmethod
    def _is_url(cover: 'str | PathLike[str]') -> bool:
        """Check if the cover is specified using either a local path or a URL.

        Returns:
            Result of checking the cover for URL format.

        """
        return bool(re.search(r'^https?://', str(cover)))

    #
    # Public methods
    #

    async def hide_keyboard(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        latest_message: 'LatestMessage',
    ) -> None:
        """Remove the keyboard from the old message, leaving the cover and
        description unchanged.
        """
        message_id = latest_message['message_id']
        chat_id = latest_message['chat_id']

        with contextlib.suppress(BadRequest):
            reply_markup = await self._create_markup_keyboard(EMPTY_KEYBOARD, None, context)
            await context.bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=reply_markup,
            )

    async def render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
        **_kwargs: 'Any',
    ) -> 'Message | tuple[Message]| None':
        """Render the screen components (i.e., cover, description and keyboard),
        and return a corresponding object of the Message type.

        Returns:
            Rendered object of `Message` type.

        Raises:
            BadRequest: If Telegram cannot process the request.
            ScreenRenderNotSupportedError: If the target screen cannot be rendered over
            the current one due to incompatible layout.

        """
        from hammett.conf import settings

        send: Callable[..., Awaitable[Any]] | None = None
        method_kwargs: Any = {}
        if config.as_new_message:
            send, method_kwargs = await self._get_new_message_render_method(context, config)
        else:
            send, method_kwargs = await self._get_edit_render_method(context, config)

        message: Message | None = None
        if send and method_kwargs:
            # Unfortunately, it's currently not possible to send a keyboard along
            # with a group of attachments
            if not config.attachments:
                method_kwargs['reply_markup'] = await self._create_markup_keyboard(
                    config.keyboard,
                    update,
                    context,
                )

            method_kwargs['read_timeout'] = settings.SEND_METHODS_READ_TIMEOUT

            try:
                send_object = await send(**method_kwargs)
            except error.BadRequest as exc:
                if exc.message == _NO_MESSAGE_TO_EDIT:
                    msg = (
                        'Unsupported screen transition due to incompatible layout. '
                        'Use covers consistently or disable them entirely.'
                    )
                    raise ScreenRenderNotSupportedError(msg) from exc

                raise

            message = send_object
            if (
                config.cover
                and config.cache_covers
                and getattr(send_object, 'photo', None)
                and not self._is_url(config.cover)
            ):
                photo_size_object = send_object.photo[-1]
                self._cached_covers[config.cover] = photo_size_object.file_id

        return message

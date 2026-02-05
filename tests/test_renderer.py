"""The module contains the tests for the renderer."""

# ruff: noqa: SLF001

import tempfile
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from telegram import InlineKeyboardMarkup, InputMediaPhoto, PhotoSize
from telegram.constants import ParseMode
from telegram.error import BadRequest

from hammett.core import Button
from hammett.core.constants import FinalRenderConfig, SourceTypes
from hammett.core.exceptions import ScreenDocumentDataIsEmpty, ScreenRenderNotSupported
from hammett.core.renderer import _NO_MESSAGE_TO_EDIT, Renderer
from hammett.test.base import BaseTestCase


class RendererTests(BaseTestCase):
    """The class implements the tests for the renderer."""

    async def test_create_input_media_document_raises_when_media_missing(self):
        """Test the case when creating document media fails due to missing media."""
        renderer = Renderer(ParseMode.HTML)
        document = {'document_kwargs': {}}

        with self.assertRaises(ScreenDocumentDataIsEmpty):
            renderer._create_input_media_document(document, 'text')

    async def test_create_markup_keyboard_with_button_rows(self):
        """Test the case when markup is created from rows with Button instances."""
        async def handler(_self, _update, _context):  # noqa: RUF029
            return None

        renderer = Renderer(ParseMode.HTML)
        keyboard = [
            [Button('First', handler, source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
            [Button('Second', handler, source_type=SourceTypes.HANDLER_SOURCE_TYPE),
            Button('Third', handler, source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
        ]
        markup = await renderer._create_markup_keyboard(keyboard, self.update, self.context)
        assert isinstance(markup, InlineKeyboardMarkup)

        inline_keyboard = markup.inline_keyboard
        assert len(inline_keyboard) == 2
        assert [b.text for b in inline_keyboard[0]] == ['First']
        assert [b.text for b in inline_keyboard[1]] == ['Second', 'Third']

    async def test_get_edit_render_method_media_kwargs_for_document(self):
        """Test the case when caption and parse mode are set for a document."""
        renderer = Renderer(ParseMode.HTML)
        media = b'media'
        caption = 'text'
        media_kwargs = await renderer._get_edit_render_method_media_kwargs(media={
                'media': media,
                'document_kwargs': {},
            },
            description=caption,
        )

        assert media_kwargs['media'].caption == caption
        assert media_kwargs['media'].parse_mode == ParseMode.HTML
        assert media_kwargs['media'].media.input_file_content == media

    async def test_get_edit_render_method_media_kwargs_for_photo_size(self):
        """Test the case when caption and parse mode are set for a PhotoSize."""
        renderer = Renderer(ParseMode.HTML)
        media = 'media'
        caption = 'text'
        media_kwargs = await renderer._get_edit_render_method_media_kwargs(
            media=PhotoSize(media, 'test', 100, 100),
            description=caption,
        )

        assert media_kwargs['media'].caption == caption
        assert media_kwargs['media'].parse_mode == ParseMode.HTML
        assert media_kwargs['media'].media == media

    async def test_get_edit_render_method_media_kwargs_with_file(self):
        """Test the case when caption and parse mode are set for a media in cache."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        with tempfile.NamedTemporaryFile(mode='w+', delete=True, encoding='utf-8') as tmp:
            tmp.write('test')
            tmp.flush()
            tmp.seek(0)

            content = tmp.read()
            media_kwargs = await renderer._get_edit_render_method_media_kwargs(
                media=tmp.file.name,
                description=caption,
            )

            assert media_kwargs['media'].caption == caption
            assert media_kwargs['media'].parse_mode == ParseMode.HTML
            assert media_kwargs['media'].media.input_file_content == content.encode()

    async def test_get_edit_render_method_media_kwargs_with_media_in_cache(self):
        """Test the case when caption and parse mode are set for a media in cache."""
        renderer = Renderer(ParseMode.HTML)
        renderer._cached_covers = {'test_id': 'test_file'}
        caption = 'text'
        media_kwargs = await renderer._get_edit_render_method_media_kwargs(
            media='test_id',
            description=caption,
        )

        assert media_kwargs['media'].caption == caption
        assert media_kwargs['media'].parse_mode == ParseMode.HTML
        assert media_kwargs['media'].media == 'test_file'

    async def test_get_edit_render_method_returns_media_sender_for_cover_url(self):
        """Test the case when edit mode uses media sender for a cover URL."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        url = 'https://example.com/image.png'
        config = FinalRenderConfig(
            description=caption,
            cover=url,
        )
        send, kwargs = await renderer._get_edit_render_method(self.context, config)

        assert send == self.context.bot.edit_message_media
        assert 'media' in kwargs
        assert isinstance(kwargs['media'], InputMediaPhoto)
        assert kwargs['media'].caption == caption
        assert url in kwargs['media'].media

    async def test_get_edit_render_method_returns_text_sender_for_text_only(self):
        """Test the case when edit mode uses text sender for description only."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        config = FinalRenderConfig(
            message_id=self.message_id,
            description=caption,
        )

        send, kwargs = await renderer._get_edit_render_method(self.context, config)

        assert send == self.context.bot.edit_message_text
        assert kwargs['text'] == caption
        assert 'parse_mode' in kwargs

    async def test_get_new_message_render_method_for_attachments(self):
        """Test the case when attachments are set."""
        renderer = Renderer(ParseMode.HTML)
        document_one = {
            'media': b'test_one',
            'document_kwargs': {},
        }
        document_two = {
            'media': b'test_two',
            'document_kwargs': {},
        }
        config = FinalRenderConfig(attachments=[document_one, document_two])
        send, media_kwargs = await renderer._get_new_message_render_method(self.context, config)

        assert send == self.context.bot.send_media_group
        assert media_kwargs['parse_mode'] == ParseMode.HTML
        assert media_kwargs['media'][0] == document_one
        assert media_kwargs['media'][1] == document_two

    async def test_get_new_message_render_method_for_document(self):
        """Test the case when caption and parse mode are set for a document."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        media = b'media'
        config = FinalRenderConfig(
            document={'media': media, 'document_kwargs': {}},
            description=caption,
        )
        send, media_kwargs = await renderer._get_new_message_render_method(self.context, config)

        assert send == self.context.bot.send_document
        assert media_kwargs['caption'] == caption
        assert media_kwargs['parse_mode'] == ParseMode.HTML
        assert media_kwargs['document'].input_file_content == media

    async def test_get_new_message_render_method_returns_photo_sender_for_cover_url(self):
        """Test the case when new message mode uses photo sender for a cover URL."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        url = 'https://example.com/image.png'
        config = FinalRenderConfig(
            description=caption,
            cover=url,
            cache_covers=True,
        )

        send, media_kwargs = await renderer._get_new_message_render_method(self.context, config)

        assert send == self.context.bot.send_photo
        assert media_kwargs['caption'] == caption
        assert media_kwargs['parse_mode'] == ParseMode.HTML
        assert url in str(media_kwargs['photo'])
        assert '?' in str(media_kwargs['photo'])

    async def test_get_new_message_render_method_returns_text_sender_for_text_only(self):
        """Test the case when new message mode uses text sender for description only."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        config = FinalRenderConfig(description=caption)
        send, media_kwargs = await renderer._get_new_message_render_method(self.context, config)

        assert send == self.context.bot.send_message
        assert media_kwargs['text'] == caption
        assert media_kwargs['parse_mode'] == ParseMode.HTML

    async def test_get_new_message_render_method_with_file(self):
        """Test the case when caption and parse mode are set for a media in cache."""
        renderer = Renderer(ParseMode.HTML)
        caption = 'text'
        with tempfile.NamedTemporaryFile(mode='w+', delete=True, encoding='utf-8') as tmp:
            send, media_kwargs = await renderer._get_new_message_render_method(
                self.context,
                config=FinalRenderConfig(
                    cover=tmp.file.name,
                    description=caption,
                    cache_covers=True,
                ),
            )

            assert send == self.context.bot.send_photo
            assert media_kwargs['caption'] == caption
            assert media_kwargs['parse_mode'] == ParseMode.HTML
            assert media_kwargs['photo'] == tmp.file.name

    async def test_hide_keyboard_sends_empty_keyboard_reply_markup(self):
        """Test hide_keyboard sends an empty keyboard via edit_message_reply_markup
        without patching bot method.
        """
        renderer = Renderer(ParseMode.HTML)
        latest_message = {
            'message_id': self.message_id,
            'chat_id': self.chat.id,
            'hide_keyboard': True,
        }

        fake_bot = SimpleNamespace(edit_message_reply_markup=AsyncMock())
        self.context._application.bot = fake_bot

        await renderer.hide_keyboard(self.context, latest_message)

        fake_bot.edit_message_reply_markup.assert_awaited_once()
        kwargs = fake_bot.edit_message_reply_markup.await_args.kwargs  # type: ignore[attr-defined]
        assert kwargs['chat_id'] == self.chat.id
        assert kwargs['message_id'] == self.message_id
        assert isinstance(kwargs['reply_markup'], InlineKeyboardMarkup)
        assert kwargs['reply_markup'].inline_keyboard == ()

    def test_is_url_detects_http_and_https(self):
        """Test the case when URLs are detected correctly."""
        assert Renderer._is_url('http://example.com/file.png')
        assert Renderer._is_url('https://example.com/file.png')
        assert not Renderer._is_url('local/file.png')

    async def test_render_caches_photo_file_id_for_local_cover(self):
        """Test the case when the photo file id is cached for a local cover."""
        renderer = Renderer(ParseMode.HTML)
        send_result = SimpleNamespace(
            photo=[SimpleNamespace(file_id='first'), SimpleNamespace(file_id='last')],
        )
        with (
            tempfile.NamedTemporaryFile(mode='w', delete=True, encoding='utf-8') as tmp,
            patch.object(
                renderer,
                '_get_edit_render_method',
                new=AsyncMock(
                    return_value=(AsyncMock(return_value=send_result), {'chat_id': self.chat_id}),
                ),
            ),
        ):
            config = FinalRenderConfig(
                cover=tmp.name,
                cache_covers=True,
            )
            await renderer.render(None, self.context, config)

            assert Renderer._cached_covers.get(tmp.name) == 'last'

    async def test_render_raises_screen_render_not_supported_when_no_message_to_edit(self):
        """Test the case when BadRequest with 'There is no text in the message to edit'
        message is raised and ScreenRenderNotSupported is raised instead.
        """
        renderer = Renderer(ParseMode.HTML)
        fake_send = AsyncMock(side_effect=BadRequest(_NO_MESSAGE_TO_EDIT))

        with (
            patch.object(
                renderer,
                '_get_edit_render_method',
                new=AsyncMock(return_value=(fake_send, {'chat_id': self.chat_id}))),
            self.assertRaises(ScreenRenderNotSupported) as exc_context,
        ):
            await renderer.render(None, self.context, FinalRenderConfig(as_new_message=False))

        assert (
            exc_context.exception.args[0]
            == 'Unsupported screen transition due to incompatible layout. '
            'Use covers consistently or disable them entirely.'
        )
        assert isinstance(exc_context.exception.__cause__, BadRequest)

    async def test_render_re_raises_bad_request_when_message_differs_from_no_message_to_edit(self):
        """Test the case when BadRequest with a different message is re-raised."""
        renderer = Renderer(ParseMode.HTML)
        error_message = 'Bad request: message is invalid'
        fake_send = AsyncMock(side_effect=BadRequest(error_message))

        with (
            patch.object(
                renderer,
                '_get_edit_render_method',
                new=AsyncMock(return_value=(fake_send, {'chat_id': self.chat_id}))),
            self.assertRaises(BadRequest) as exc_context,
        ):
            await renderer.render(None, self.context, FinalRenderConfig(as_new_message=False))

        assert exc_context.exception.message == error_message

    async def test_render_uses_new_message_render_method_when_as_new_message_true(self):
        """Test that render delegates to _get_new_message_render_method
        when as_new_message is True.
        """
        renderer = Renderer(ParseMode.HTML)
        fake_send = AsyncMock(return_value=SimpleNamespace())

        with patch.object(
            renderer,
            '_get_new_message_render_method',
            new=AsyncMock(return_value=(fake_send, {'chat_id': self.chat_id})),
        ) as mocked_get_new:
            await renderer.render(None, self.context, FinalRenderConfig(as_new_message=True))

            mocked_get_new.assert_awaited_once()
            fake_send.assert_awaited_once()
            kwargs = fake_send.await_args.kwargs
            assert kwargs['chat_id'] == self.chat_id
            assert isinstance(kwargs['reply_markup'], InlineKeyboardMarkup)

    async def test_render_uses_edit_message_render_method_when_as_new_message_false(self):
        """Test that render delegates to _get_edit_render_method when as_new_message is False."""
        renderer = Renderer(ParseMode.HTML)
        fake_send = AsyncMock(return_value=SimpleNamespace())

        with patch.object(
            renderer,
            '_get_edit_render_method',
            new=AsyncMock(return_value=(fake_send, {'chat_id': self.chat_id})),
        ) as mocked_get_new:
            await renderer.render(None, self.context, FinalRenderConfig(as_new_message=False))

            mocked_get_new.assert_awaited_once()
            fake_send.assert_awaited_once()
            kwargs = fake_send.await_args.kwargs
            assert kwargs['chat_id'] == self.chat_id
            assert isinstance(kwargs['reply_markup'], InlineKeyboardMarkup)

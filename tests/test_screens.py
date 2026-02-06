"""The module contains the tests for the screens."""

# ruff: noqa: S106, SLF001

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.constants import LATEST_SENT_MSG_KEY, RenderConfig
from hammett.core.exceptions import (
    FailedToGetDataAttributeOfQueryError,
    PayloadIsEmptyError,
    ScreenDescriptionIsEmptyError,
)
from hammett.core.persistence import RedisPersistence
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config, override_settings
from tests.base import (
    CHAT_ID,
    MESSAGE_ID,
    USER_ID,
    BaseTestScreenWithDescription,
    BaseTestScreenWithHideKeyboard,
    BaseTestScreenWithMockedRenderer,
    TestScreen,
)

_DATA = {'key1': 'value1', 'key2': 'value2'}


class TestScreenWithMockedRendererAndHideKeyboard(
    BaseTestScreenWithMockedRenderer,
    BaseTestScreenWithDescription,
    BaseTestScreenWithHideKeyboard,
):
    """The class represents the base screen for the testing purposes."""


class TestScreenWithoutDescription(Screen):
    """The class implements a screen without a description."""


class ScreenTests(BaseTestCase):
    """The class implements the tests for the screens."""

    async def test_add_default_keyboard_called_when_keyboard_is_none(self):
        """Test that add_default_keyboard is called when keyboard is None in config."""
        screen = TestScreen()
        config = RenderConfig(description=TestScreen.description, keyboard=None)

        with patch.object(screen, 'add_default_keyboard') as mock_add_default_keyboard:
            await screen.render(self.update, self.context, config=config)
            mock_add_default_keyboard.assert_awaited_once()

    async def test_add_default_keyboard_not_called_when_keyboard_is_empty(self):
        """Test that add_default_keyboard is not called when keyboard is an empty list in config."""
        screen = TestScreen()
        config = RenderConfig(description=TestScreen.description, keyboard=[])

        with patch.object(screen, 'add_default_keyboard') as mock_add_default_keyboard:
            await screen.render(self.update, self.context, config=config)
            mock_add_default_keyboard.assert_not_called()

    async def test_default_getter_methods_return_class_defaults(self):
        """Test getters return default values from Screen attributes."""
        screen = TestScreen()

        assert not await screen.get_cache_covers(self.update, self.context)
        assert not await screen.get_cover(self.update, self.context)
        assert await screen.get_document(self.update, self.context) is None
        assert not await screen.get_hide_keyboard(self.update, self.context)

    async def test_get_config_returns_default_render_config(self):
        """Test that get_config returns the default RenderConfig instance."""
        screen = TestScreen()
        config = await screen.get_config(self.update, self.context)

        assert config == RenderConfig()

    async def test_get_payload_raises_when_query_has_no_data(self):
        """Test the case when getting payload fails because query has no data."""
        with (
            patch('hammett.utils.misc.get_callback_query', return_value=SimpleNamespace(data=None)),
            self.assertRaises(FailedToGetDataAttributeOfQueryError),
        ):
            await Screen.get_payload(self.update, self.context)

    async def test_get_payload_raises_when_payload_not_found(self):
        """Test the case when getting payload fails because it is not found in storage."""
        with (
            patch(
                'hammett.core.screen.get_callback_query',
                return_value=SimpleNamespace(data='key'),
            ),
            self.assertRaises(PayloadIsEmptyError),
        ):
            await Screen.get_payload(self.update, self.context)

    async def test_get_payload_returns_value(self):
        """Test the case when getting payload succeeds and returns value from storage."""
        storage = {'key': 'value'}
        with (
            patch(
                'hammett.core.screen.get_callback_query',
                return_value=SimpleNamespace(data='key'),
            ),
            patch('hammett.core.handlers.get_payload_storage', return_value=storage),
        ):
            value = await Screen.get_payload(self.update, self.context)

        assert value == 'value'
        assert 'key' not in storage

    def test_getting_existing_current_state(self):
        """Test getting the existing current state."""
        state_value = 'custom_state'
        self.context.user_data['current_state'] = state_value

        assert Screen.get_current_state(self.context) == state_value

    def test_getting_non_existing_current_state(self):
        """Test getting the existing current state."""
        assert Screen.get_current_state(self.context) is None

    @catch_render_config()
    async def test_jump_sets_as_new_message_true(self, actual):
        """Test that jump sets as_new_message to True and uses default config."""
        screen = TestScreen()
        await screen.jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreen.description,
            as_new_message=True,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_message_id_extracted_from_callback_query_when_missing(self, actual):
        """Test message_id is populated from callback query when not provided in config."""
        message_id = 123
        with patch('hammett.core.screen.get_callback_query', return_value=SimpleNamespace(
            message=SimpleNamespace(message_id=message_id),
            data='test',
        )):
            await TestScreen().move(self.update, self.context)

        assert actual.final_render_config.message_id == message_id

    @catch_render_config()
    async def test_move_uses_default_config_without_as_new_message(self, actual):
        """Test that move uses default config and does not set as_new_message."""
        screen = TestScreen()
        await screen.move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreen.description,
            as_new_message=False,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    async def test_post_render_uses_last_message_from_tuple(self):
        """Test that _post_render picks the last message when renderer returns a tuple."""
        screen = TestScreen()

        first = SimpleNamespace(message_id=111, chat_id=CHAT_ID)
        last = self.message
        with (
            patch.object(screen.renderer, 'render', new=AsyncMock(return_value=(first, last))),
            patch('hammett.core.screen.get_latest_message') as mock_get_latest_message,
        ):
            await screen.send(self.context)
            mock_get_latest_message.assert_called_once_with(self.context, last)

    async def test_previous_message_keyboard_hidden_on_new_message(self):
        """Test hiding the previous message's keyboard when sending a new message."""
        screen = TestScreen()
        config = RenderConfig(
            as_new_message=True,
            description=TestScreen.description,
            hide_keyboard=True,
        )

        latest_message = {'chat_id': CHAT_ID, 'message_id': MESSAGE_ID, 'hide_keyboard': True}
        with (
            patch('hammett.core.screen.get_latest_message', return_value=latest_message),
            patch.object(screen.renderer, 'hide_keyboard', new=AsyncMock()) as mock_hide_keyboard,
            patch.object(
                screen.renderer,
                'render',
                new=AsyncMock(return_value=SimpleNamespace(photo=None)),
            ),
        ):
            await screen.render(self.update, self.context, config=config)
            mock_hide_keyboard.assert_awaited_once_with(self.context, latest_message)

    async def test_screen_without_description(self):
        """Test the case when a description of a screen is empty."""
        screen = TestScreenWithoutDescription()
        with self.assertRaises(ScreenDescriptionIsEmptyError):
            await screen.move(self.update, self.context)

    @catch_render_config()
    async def test_send_sets_as_new_message_and_uses_default_config(self, actual):
        """Test that send sets as_new_message and uses default config values."""
        screen = TestScreen()
        await screen.send(self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreen.description,
            as_new_message=True,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_send_uses_passed_config_priority(self, actual):
        """Test that explicitly passed config has higher priority than defaults."""
        screen = TestScreen()
        custom_config = RenderConfig(
            description='Overridden description',
            keyboard=[],
        )

        await screen.send(self.context, config=custom_config)

        expected = self.prepare_final_render_config(RenderConfig(
            description='Overridden description',
            keyboard=[],
            as_new_message=True,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    def test_singleton_behavior_for_screen(self):
        """Test the case when Screen subclasses follow singleton pattern."""
        first = TestScreen()
        second = TestScreen()

        assert first is second

    @override_settings(SAVE_LATEST_MESSAGE=False)
    async def test_warning_logged_when_hide_keyboard_without_save_latest_message(self):
        """Test the case when a warning is logged when SAVE_LATEST_MESSAGE is False
        and hide_keyboard is True.
        """
        screen = TestScreen()
        config = RenderConfig(hide_keyboard=True, description=TestScreen.description)

        with (
            self.assertLogs('hammett.core.screen', level='WARNING') as log,
            patch.object(screen.renderer, 'render', new=AsyncMock(return_value=object())),
        ):
            await screen.render(self.update, self.context, config=config)

        assert len(log.records) == 1
        assert 'SAVE_LATEST_MESSAGE setting set to True' in log.records[0].message


class ScreenTestsWithoutUpdate(BaseTestCase):
    """The class implements the tests for the screens without update."""

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    @override_settings(SAVE_LATEST_MESSAGE=True, TOKEN='secret-token')
    async def test_updating_user_data_after_sending_notification_with_hiding_keyboard(self):
        """Test updating the user_data when a screen is sent as a notification
        with hiding keyboard.
        """
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()
        self.context._application.user_data = {USER_ID: _DATA}

        await TestScreenWithMockedRendererAndHideKeyboard().send(self.context)

        updated_user_data = self.context._application.persistence.user_data
        assert updated_user_data == {
            USER_ID: {
                LATEST_SENT_MSG_KEY: {
                    'hide_keyboard': True,
                    'message_id': MESSAGE_ID,
                    'chat_id': CHAT_ID,
                },
                **_DATA,
            },
        }

        await self.context._application.persistence.redis_cli.aclose()

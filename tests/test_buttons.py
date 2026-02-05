"""The module contains the tests for buttons."""

from telegram import InlineKeyboardButton, User
from telegram.ext import CallbackContext

from hammett.core import handlers
from hammett.core.button import Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.exceptions import UnknownSourceType
from hammett.test.base import BaseTestCase
from tests.base import TestRouteScreen, TestScreen

_BUTTON_KWARGS = {
    'caption': 'Test',
    'source': TestScreen,
    'source_type': SourceTypes.MOVE_SOURCE_TYPE,
}


class ButtonsTests(BaseTestCase):
    """The class implements the tests for buttons."""

    url = 'https://example.org/app'

    def test_button_equality(self):
        """Test comparing two Buttons with each other."""
        button_one = Button(**_BUTTON_KWARGS)
        button_two = Button(**_BUTTON_KWARGS)

        assert button_one == button_two

    def test_button_equality_with_non_button(self):
        """Test comparing a Button with a non-Button object."""
        button = Button(**_BUTTON_KWARGS)
        assert button != object()

    def test_button_hash(self):
        """Test hashing a Button instance."""
        button = Button(**_BUTTON_KWARGS)
        assert isinstance(hash(button), int)

    async def test_create_handler_button(self):
        """Test creating a button with HANDLER_SOURCE_TYPE."""
        async def handler(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        caption = 'Test'
        button = Button(caption, handler, source_type=SourceTypes.HANDLER_SOURCE_TYPE)
        inline_button, _ = await button.create(self.update, self.context)

        expected_data = (
            f'{handlers.calc_checksum(handler)},'
            f'button={handlers.calc_checksum(caption)},'
            f'user_id={self.user_id}'
        )
        assert inline_button.callback_data == expected_data
        assert isinstance(inline_button, InlineKeyboardButton)

    async def test_create_handler_button_with_payload_and_update_none(self):
        """Test creating a handler button with payload when update is None."""
        async def handler(_self, _update, _context):  # noqa: RUF029
            return DEFAULT_STATE

        caption = 'Test'
        button = Button(
            caption,
            handler,
            source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            payload='payload',
        )
        expected_data = (
            f'{handlers.calc_checksum(handler)},'
            f'button={handlers.calc_checksum(caption)},'
            f'user_id={self.context._user_id}'  # noqa: SLF001
        )

        inline_button, _ = await button.create(None, self.context)
        assert inline_button.callback_data == expected_data
        assert isinstance(inline_button, InlineKeyboardButton)

        storage = handlers.get_payload_storage(self.context)
        assert storage[expected_data] == 'payload'

    async def test_create_url_button(self):
        """Test creating a button with URL_SOURCE_TYPE."""
        button = Button('Open', self.url, source_type=SourceTypes.URL_SOURCE_TYPE)
        inline_button, _ = await button.create(self.update, self.context)

        assert isinstance(inline_button, InlineKeyboardButton)
        assert inline_button.url == self.url

    async def test_create_uses_source_shortcut_if_it_already_set(self):
        """Test that the shortcut handler's checksum is used if it's already set."""
        button = Button(**_BUTTON_KWARGS)
        handler_checksum = handlers.calc_checksum(getattr(button, 'source_shortcut', None))
        inline_button, _ = await button.create(self.update, self.context)

        assert handler_checksum in inline_button.callback_data

    async def test_create_web_app_button(self):
        """Test creating a button with WEB_APP_SOURCE_TYPE."""
        button = Button('WebApp', self.url, source_type=SourceTypes.WEB_APP_SOURCE_TYPE)
        inline_button, _ = await button.create(self.update, self.context)

        assert isinstance(inline_button, InlineKeyboardButton)
        assert inline_button.web_app.url == self.url

    async def test_mapping_shortcuts_for_jump_along_route_and_move_along_route(self):
        """Test that source_shortcut is set for the JUMP_ALONG_ROUTE and
        MOVE_ALONG_ROUTE shortcut types.
        """
        jump_button = Button(
            'Jump',
            TestRouteScreen,
            source_type=SourceTypes.JUMP_ALONG_ROUTE_SOURCE_TYPE,
        )
        assert callable(getattr(jump_button, 'source_shortcut', None))
        assert jump_button.source_shortcut.__name__ == 'jump_along_route'

        move_button = Button(
            'Move',
            TestRouteScreen,
            source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
        )
        assert callable(getattr(move_button, 'source_shortcut', None))
        assert move_button.source_shortcut.__name__ == 'move_along_route'

    async def test_mapping_shortcuts_for_jump_and_move(self):
        """Test that source_shortcut is set for the jump and move shortcut types."""
        jump_button = Button('Jump', TestScreen, source_type=SourceTypes.JUMP_SOURCE_TYPE)
        assert callable(getattr(jump_button, 'source_shortcut', None))
        assert jump_button.source_shortcut.__name__ == 'jump'

        move_button = Button('Move', TestScreen, source_type=SourceTypes.MOVE_SOURCE_TYPE)
        assert callable(getattr(move_button, 'source_shortcut', None))
        assert move_button.source_shortcut.__name__ == 'move'

    async def test_non_callable_source_as_handler(self):
        """Test the case when a button handler is not callable."""
        with self.assertRaises(TypeError):
            Button(
                'Test',
                None,  # is not callable, so it's invalid
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            )

    async def test_unknown_source_type(self):
        """Test the case when an unknown source type passed."""
        unknown_source_type = 100
        with self.assertRaises(UnknownSourceType):
            button = Button(
                'Test',
                TestScreen,
                source_type=unknown_source_type,
            )
            await button.create(self.update, self.context)

    async def test_using_random_class_instead_of_screen_for_move(self):
        """Test the case when the source type is `MOVE_SOURCE_TYPE` but
        the source isn't a subclass of Screen.
        """

        class AnythingElseButScreen:
            """A dummy class used for the testing purposes."""

        with self.assertRaises(TypeError):
            Button(
                'Test',
                AnythingElseButScreen,  # is not a subclass of Screen, so it's invalid
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )


class TestGetUserId(BaseTestCase):
    """The class contains tests for the _get_user_id utility function."""

    _user_id_in_context = 123
    _user_id_in_update = 456

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            user_id=self._user_id_in_context,
        )

    def get_user(self):
        """Return the `User` object for testing purposes."""
        return User(self._user_id_in_update, 'TestUser', is_bot=False)

    async def test_get_user_id_with_update_none(self):
        """Test that _get_user_id returns user id from context when Update is None."""
        user_id = Button._get_user_id(None, self.context)  # noqa: SLF001
        assert user_id == self._user_id_in_context

    async def test_get_user_id_with_update_present(self):
        """Test that _get_user_id returns user id from Update when present."""
        user_id = Button._get_user_id(self.update, self.context)  # noqa: SLF001
        assert user_id == self._user_id_in_update

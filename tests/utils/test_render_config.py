"""The module contains tests for the render config helpers."""

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.constants import LATEST_SENT_MSG_KEY, FinalRenderConfig
from hammett.core.exceptions import MissingPersistence
from hammett.core.persistence import RedisPersistence
from hammett.test.base import BaseTestCase
from hammett.utils.render_config import get_latest_message, save_latest_message


class UtilsRenderConfigTests(BaseTestCase):
    """The class implements the tests for the render config helpers."""

    async def test_get_latest_message_from_context_user_data(self):
        """Test retrieving the latest message from context.user_data."""
        expected = {
            'hide_keyboard': True,
            'message_id': self.message.message_id,
            'chat_id': self.message.chat_id,
        }
        self.context.user_data.update({LATEST_SENT_MSG_KEY: expected})

        actual = get_latest_message(self.context, self.message)
        assert actual == expected

    async def test_get_latest_message_returns_none_when_absent(self):
        """Test returning None when there is no stored latest message."""
        self.context.user_data.clear()
        self.context._application.user_data = {self.message.chat_id: {}}  # noqa: SLF001

        actual = get_latest_message(self.context, self.message)
        assert actual is None

    async def test_save_latest_message_writes_to_context_user_data(self):
        """Test saving the latest message into context.user_data."""
        self.context.user_data.clear()
        config = FinalRenderConfig(hide_keyboard=True)

        await save_latest_message(self.context, config, self.message)

        assert LATEST_SENT_MSG_KEY in self.context.user_data
        assert self.context.user_data[LATEST_SENT_MSG_KEY] == {
            'hide_keyboard': True,
            'message_id': self.message.message_id,
            'chat_id': self.message.chat_id,
        }


class UtilsRenderConfigTestsWithoutUpdate(BaseTestCase):
    """The class implements the tests for the render config helpers without update."""

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    async def test_get_latest_message_from_persistence_when_keyerror(self):
        """Test retrieving the latest message from persistence on KeyError."""
        self.context._application.persistence = RedisPersistence()  # noqa: SLF001
        self.context._application.persistence.redis_cli = FakeAsyncRedis()  # noqa: SLF001
        self.context._application.user_data = {}  # noqa: SLF001

        actual = get_latest_message(self.context, self.message)
        assert actual is None

    async def test_get_latest_message_from_persistence_when_typeerror(self):
        """Test retrieving the latest message from persistence on TypeError."""
        expected = {
            'hide_keyboard': False,
            'message_id': self.message.message_id,
            'chat_id': self.message.chat_id,
        }

        self.context._application.persistence = RedisPersistence()  # noqa: SLF001
        self.context._application.persistence.redis_cli = FakeAsyncRedis()  # noqa: SLF001
        self.context._application.user_data = {  # noqa: SLF001
            self.message.chat_id: {LATEST_SENT_MSG_KEY: expected},
        }

        actual = get_latest_message(self.context, self.message)

        assert actual == expected

    async def test_save_latest_message_raises_without_persistence_on_typeerror(self):
        """Test raising MissingPersistence when no persistence is configured."""
        self.context._application.persistence = None  # noqa: SLF001

        with self.assertRaises(MissingPersistence):
            await save_latest_message(self.context, FinalRenderConfig(), self.message)

    async def test_save_latest_message_updates_persistence_on_typeerror(self):
        """Test saving the latest message using persistence on TypeError."""
        self.context._application.persistence = RedisPersistence()  # noqa: SLF001
        self.context._application.persistence.redis_cli = FakeAsyncRedis()  # noqa: SLF001
        self.context._application.user_data = {  # noqa: SLF001
            self.message.chat_id: {},
        }

        config = FinalRenderConfig(hide_keyboard=False)
        await save_latest_message(self.context, config, self.message)

        updated_user_data = self.context._application.persistence.user_data  # noqa: SLF001
        assert updated_user_data == {
            self.message.chat_id: {
                LATEST_SENT_MSG_KEY: {
                    'hide_keyboard': False,
                    'message_id': self.message.message_id,
                    'chat_id': self.message.chat_id,
                },
            },
        }

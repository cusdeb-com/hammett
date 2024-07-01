"""The module contains the tests for the persistence."""

# ruff: noqa: ANN201, SLF001

import json

from fakeredis import FakeAsyncRedis

from hammett.core.persistence import RedisPersistence
from hammett.test.base import BaseTestCase

_BOT_NAME = 'test'

_CHAT_ID = 123456789

_DATA = {'key1': 'value1', 'key2': 'value2'}

_NEW_STATE = 'new_state'

_USER_ID = 123456789


class PersistenceTests(BaseTestCase):
    """The class implements the tests for the persistence."""

    def setUp(self):
        """Initialize a persistence object and replace its Redis instance
        with a fake one.
        """
        self.persistence = RedisPersistence()
        self.persistence.redis_cli = FakeAsyncRedis()

    async def test_decoding_and_encoding_of_conversations_object(self):
        """Test decoding and encoding of the conversations object."""
        conversations = {
            _BOT_NAME: {
                (_CHAT_ID, _USER_ID): 'state',
            },
        }

        encoded_conversation = self.persistence._encode_conversations(conversations)
        self.assertEqual(
            encoded_conversation,
            f'{{"{_BOT_NAME}": {{"[{_CHAT_ID}, {_USER_ID}]": "state"}}}}',
        )

        decoded_conversation = self.persistence._decode_conversations(encoded_conversation)
        self.assertEqual(decoded_conversation, conversations)

    async def test_decoding_of_data(self):
        """Test decoding of the data."""
        decoded_data = self.persistence._decode_data({
            str(_USER_ID): json.dumps(_DATA).encode('utf-8'),
        })
        self.assertDictEqual(decoded_data, {_USER_ID: _DATA})

    async def test_getting_and_setting_of_bot_data(self):
        """Test getting and setting of the bot_data."""
        bot_data = await self.persistence.get_bot_data()
        self.assertEqual(bot_data, {})

        await self.persistence.update_bot_data(_DATA)
        updated_bot_data = await self.persistence.get_bot_data()
        self.assertEqual(updated_bot_data, _DATA)

    async def test_getting_and_setting_of_callback_data(self):
        """Test getting and setting of the callback_data."""
        callback_data = await self.persistence.get_callback_data()
        self.assertIsNone(callback_data)

        await self.persistence.update_callback_data(([], _DATA))
        updated_callback_data = await self.persistence.get_callback_data()
        self.assertEqual(updated_callback_data, ([], _DATA))

    async def test_getting_and_setting_of_conversations_object(self):
        """Test getting and setting of the conversations object."""
        conversations = await self.persistence.get_conversations(_BOT_NAME)
        self.assertEqual(conversations, {})

        await self.persistence.update_conversation(
            _BOT_NAME, (_CHAT_ID, _USER_ID), _NEW_STATE,
        )
        updated_conversations = await self.persistence.get_conversations(_BOT_NAME)
        self.assertEqual(updated_conversations, {(_CHAT_ID, _USER_ID): _NEW_STATE})

    async def test_getting_setting_and_dropping_of_chat_data(self):
        """Test getting, setting and dropping of the chat_data."""
        chat_data = await self.persistence.get_chat_data()
        self.assertEqual(chat_data, {})

        await self.persistence.update_chat_data(_CHAT_ID, _DATA)
        updated_chat_data = await self.persistence.get_chat_data()
        self.assertEqual(updated_chat_data, {_CHAT_ID: _DATA})

        await self.persistence.drop_chat_data(_CHAT_ID)
        dropped_chat_data = await self.persistence.get_chat_data()
        self.assertEqual(dropped_chat_data, {})

    async def test_getting_setting_and_dropping_of_user_data(self):
        """Test getting, setting and dropping of the user_data."""
        user_data = await self.persistence.get_user_data()
        self.assertEqual(user_data, {})

        await self.persistence.update_user_data(_USER_ID, _DATA)
        updated_user_data = await self.persistence.get_user_data()
        self.assertEqual(updated_user_data, {_USER_ID: _DATA})

        await self.persistence.drop_user_data(_USER_ID)
        dropped_user_data = await self.persistence.get_user_data()
        self.assertEqual(dropped_user_data, {})

    async def test_hgetall_by_chunks_method(self):
        """Test a hgetall_by_chunks persistence method."""
        data = {_USER_ID: _DATA}
        await self.persistence._hsetall_data('test_key', data)

        encoded_data = await self.persistence._hgetall_by_chunks('test_key')
        decoded_data = self.persistence._decode_data(encoded_data)
        self.assertEqual(decoded_data, data)

    async def test_storing_of_data_after_flushing_database(self):
        """Test storing of the data after flushing the database."""
        await self.persistence.update_bot_data(_DATA)
        await self.persistence.update_callback_data(([], _DATA))
        await self.persistence.update_conversation(
            _BOT_NAME, (_CHAT_ID, _USER_ID), _NEW_STATE,
        )
        await self.persistence.update_chat_data(_CHAT_ID, _DATA)
        await self.persistence.update_user_data(_USER_ID, _DATA)

        await self.persistence.flush()

        self.assertEqual(self.persistence.bot_data, _DATA)
        self.assertEqual(self.persistence.callback_data, ([], _DATA))
        self.assertEqual(self.persistence.conversations, {
            _BOT_NAME: {
                (_CHAT_ID, _USER_ID): _NEW_STATE,
            },
        })
        self.assertEqual(self.persistence.chat_data, {_CHAT_ID: _DATA})
        self.assertEqual(self.persistence.user_data, {_USER_ID: _DATA})

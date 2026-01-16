"""The module contains the tests for the persistence."""

# ruff: noqa: SLF001

import json
from pathlib import Path

from fakeredis import FakeAsyncRedis

from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.persistence import RedisPersistence, _Encoder
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from hammett.types.core import State
from tests.base import CHAT_ID, USER_ID

_BOT_NAME = 'test'

_DATA = {'key1': 'value1', 'key2': 'value2'}

_NEW_STATE = State('new_state')

_TEST_KEY = State('test_key')


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
                (CHAT_ID, USER_ID): 'state',
            },
        }

        encoded_conversation = self.persistence._encode_conversations(conversations)
        self.assertEqual(
            encoded_conversation,
            f'{{"{_BOT_NAME}": {{"[{CHAT_ID}, {USER_ID}]": "state"}}}}',
        )

        decoded_conversation = self.persistence._decode_conversations(encoded_conversation)
        self.assertEqual(decoded_conversation, conversations)

    async def test_decoding_of_data(self):
        """Test decoding of the data."""
        decoded_data = self.persistence._decode_and_cast_keys(
            {str(USER_ID): json.dumps(_DATA).encode('utf-8')},
            int,
        )
        self.assertDictEqual(decoded_data, {USER_ID: _DATA})

    async def test_decoding_of_data_keeps_key_type(self):
        """Test decoding of the data without key type conversion."""
        decoded_data = self.persistence._decode_and_cast_keys({
            USER_ID: json.dumps(_DATA).encode('utf-8'),
        })
        self.assertDictEqual(decoded_data, {USER_ID: _DATA})

    async def test_dropping_of_empty_chat_data(self):
        """Test dropping of the empty chat_data."""
        await self.persistence.drop_chat_data(CHAT_ID)
        self.assertIsNone(self.persistence.user_data)

    async def test_dropping_of_empty_user_data(self):
        """Test dropping of the empty user_data."""
        await self.persistence.drop_user_data(USER_ID)
        self.assertIsNone(self.persistence.user_data)

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
            _BOT_NAME, (CHAT_ID, USER_ID), _NEW_STATE,
        )
        updated_conversations = await self.persistence.get_conversations(_BOT_NAME)
        self.assertEqual(updated_conversations, {(CHAT_ID, USER_ID): _NEW_STATE})

    async def test_getting_data_from_database_directly(self):
        """Test getting a data from a database directly."""
        await self.persistence._set_data(_TEST_KEY, _DATA)

        data = await self.persistence._get_data(_TEST_KEY)
        self.assertEqual(data, _DATA)

    async def test_getting_setting_and_dropping_of_chat_data(self):
        """Test getting, setting and dropping of the chat_data."""
        chat_data = await self.persistence.get_chat_data()
        self.assertEqual(chat_data, {})

        await self.persistence.update_chat_data(CHAT_ID, _DATA)
        updated_chat_data = await self.persistence.get_chat_data()
        self.assertEqual(updated_chat_data, {CHAT_ID: _DATA})

        await self.persistence.drop_chat_data(CHAT_ID)
        dropped_chat_data = await self.persistence.get_chat_data()
        self.assertEqual(dropped_chat_data, {})

    async def test_getting_setting_and_dropping_of_user_data(self):
        """Test getting, setting and dropping of the user_data."""
        user_data = await self.persistence.get_user_data()
        self.assertEqual(user_data, {})

        await self.persistence.update_user_data(USER_ID, _DATA)
        updated_user_data = await self.persistence.get_user_data()
        self.assertEqual(updated_user_data, {USER_ID: _DATA})

        await self.persistence.drop_user_data(USER_ID)
        dropped_user_data = await self.persistence.get_user_data()
        self.assertEqual(dropped_user_data, {})

    async def test_handling_of_error_when_getting_data(self):
        """Test the case when an error is raised when getting data."""
        encoded_data = json.dumps(_DATA) + '1'
        await self.persistence.redis_cli.set(_TEST_KEY, encoded_data)

        decoded_data = await self.persistence._get_data(_TEST_KEY)
        self.assertIsNone(decoded_data)

    async def test_hgetall_by_chunks_method(self):
        """Test a hgetall_by_chunks persistence method."""
        data = {USER_ID: _DATA}
        await self.persistence._hsetall_data('test_key', data)

        encoded_data = await self.persistence._hgetall_by_chunks('test_key')
        decoded_data = self.persistence._decode_and_cast_keys(encoded_data, int)
        self.assertEqual(decoded_data, data)

    @override_settings(REDIS_PERSISTENCE={})
    def test_initialization_without_db_specified(self):
        """Test an initialization without specifying DB attribute."""
        with self.assertRaises(ImproperlyConfigured):
            RedisPersistence()

    def test_passing_path_type_object_to_custom_encoder(self):
        """Test passing a Path type object to a custom encoder."""
        path = json.dumps(Path('/path/to/hammett'), cls=_Encoder)
        self.assertEqual('/path/to/hammett', json.loads(path))

    def test_passing_unsupported_type_to_custom_encoder(self):
        """Test passing an unsupported type to a custom encoder."""
        with self.assertRaises(TypeError):
            json.dumps(b'test', cls=_Encoder)

    async def test_storing_of_data_after_flushing_database(self):
        """Test storing of the data after flushing the database."""
        await self.persistence.update_bot_data(_DATA)
        await self.persistence.update_callback_data(([], _DATA))
        await self.persistence.update_conversation(
            _BOT_NAME, (CHAT_ID, USER_ID), _NEW_STATE,
        )
        await self.persistence.update_chat_data(CHAT_ID, _DATA)
        await self.persistence.update_user_data(USER_ID, _DATA)

        await self.persistence.flush()

        self.assertEqual(self.persistence.bot_data, _DATA)
        self.assertEqual(self.persistence.callback_data, ([], _DATA))
        self.assertEqual(self.persistence.conversations, {
            _BOT_NAME: {
                (CHAT_ID, USER_ID): _NEW_STATE,
            },
        })
        self.assertEqual(self.persistence.chat_data, {CHAT_ID: _DATA})
        self.assertEqual(self.persistence.user_data, {USER_ID: _DATA})

    async def test_updating_persistence_data_when_it_is_up_to_date(self):
        """Test updating chat_data when it is up-to-date."""
        await self.persistence.update_bot_data(_DATA)
        await self.persistence.update_bot_data(_DATA)
        self.assertEqual(self.persistence.bot_data, _DATA)

        await self.persistence.update_callback_data(([], _DATA))
        await self.persistence.update_callback_data(([], _DATA))
        self.assertEqual(self.persistence.callback_data, ([], _DATA))

        await self.persistence.update_conversation(
            _BOT_NAME, (CHAT_ID, USER_ID), _NEW_STATE,
        )
        await self.persistence.update_conversation(
            _BOT_NAME, (CHAT_ID, USER_ID), _NEW_STATE,
        )
        self.assertEqual(self.persistence.conversations, {
            _BOT_NAME: {
                (CHAT_ID, USER_ID): _NEW_STATE,
            },
        })

        await self.persistence.update_chat_data(CHAT_ID, _DATA)
        await self.persistence.update_chat_data(CHAT_ID, _DATA)
        self.assertEqual(self.persistence.chat_data, {CHAT_ID: _DATA})

        await self.persistence.update_user_data(USER_ID, _DATA)
        await self.persistence.update_user_data(USER_ID, _DATA)
        self.assertEqual(self.persistence.user_data, {USER_ID: _DATA})

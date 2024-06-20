"""The module contains the implementation of BasePersistence to make
the bots based on Hammett persistent, storing their data in Redis.
"""

import base64
import contextlib
import json
import logging
import pickle
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, cast

import redis.asyncio as redis
from redis.exceptions import ConnectionError
from telegram.ext import BasePersistence, ContextTypes
from telegram.ext._utils.types import BD, CD, UD

from hammett.conf import settings
from hammett.core.exceptions import ImproperlyConfigured

if TYPE_CHECKING:
    from typing import Any

    from telegram.ext import PersistenceInput
    from telegram.ext._utils.types import CDCData, ConversationDict, ConversationKey
    from typing_extensions import Self


LOGGER = logging.getLogger(__name__)


class _Decoder(json.JSONDecoder):
    """The class implements a custom decoder."""

    def __init__(self: 'Self', *args: 'Any', **kwargs: 'Any') -> None:
        """Initialize the decoder object."""
        super().__init__(*args, **kwargs, object_hook=self.object_hook)

    def object_hook(self: 'Self', obj: object) -> object:
        """Decode the object."""
        if isinstance(obj, dict) and obj.get('data'):
            return {
                'data': base64.b64decode(obj['data']),
                'name': obj['name'],
            }

        return obj


class _Encoder(json.JSONEncoder):
    """The class implements a custom encoder."""

    def default(self: 'Self', obj: 'Any') -> 'Any':
        """Handle encoding some objects that cannot be serialized into JSON."""
        if isinstance(obj, Path):
            return str(obj)

        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')

        return super().default(obj)


class RedisPersistence(BasePersistence[UD, CD, BD]):
    """The class implements the asynchronous interface for making
    the bots based on Hammett persistent. The data is stored in Redis.
    """

    _BOT_DATA_KEY = 'bot_data'
    _CHAT_DATA_KEY = 'chat_data'
    _USER_DATA_KEY = 'user_data'
    _CALLBACK_DATA_KEY = 'callback_data'
    _CONVERSATIONS_KEY = 'conversations'

    def __init__(
        self: 'Self',
        store_data: 'PersistenceInput | None' = None,
        on_flush: bool = False,  # noqa: FBT001,FBT002
        update_interval: float = 60,
        context_types: 'ContextTypes[Any, UD, CD, BD] | None' = None,
    ) -> None:
        """Initialize a redis persistence object."""
        super().__init__(
            store_data=store_data,  # type: ignore[arg-type]
            update_interval=update_interval,
        )

        try:
            self.redis_cli: redis.Redis[Any] = redis.Redis(
                host=settings.REDIS_PERSISTENCE.get('HOST'),
                port=settings.REDIS_PERSISTENCE.get('PORT'),
                db=settings.REDIS_PERSISTENCE['DB'],
                password=settings.REDIS_PERSISTENCE.get('PASSWORD'),
                unix_socket_path=settings.REDIS_PERSISTENCE.get('UNIX_SOCKET_PATH'),
            )
        except KeyError as exc:
            msg = f'{exc.args[0]} is missing in the REDIS_PERSISTENCE setting.'
            raise ImproperlyConfigured(msg) from exc

        self.bot_data: BD | None = None
        self.callback_data: CDCData | None = None
        self.chat_data: defaultdict[int, CD] | None = None
        self.conversations: dict[str, dict[tuple[str | int, ...], object]] | None = None
        self.context_types = cast('ContextTypes[Any, UD, CD, BD]', context_types or ContextTypes())
        self.on_flush = on_flush
        self.user_data: dict[int, UD] | None = None

    #
    # Private methods
    #

    async def _get_data(self: 'Self', key: str) -> 'Any':
        """Fetch the data from the database by the specified key."""
        try:
            redis_data = await self.redis_cli.get(key)
            if redis_data:
                return pickle.loads(redis_data)  # noqa: S301
        except (ConnectionError, pickle.UnpicklingError):
            LOGGER.exception('Failed to get the data from Redis by the key %s', key)
            return None
        else:
            return redis_data

    def _decode_data(self: 'Self', data: dict[bytes, bytes]) -> dict[int, 'UD']:
        """Return decoded data."""
        decoded_data = {}
        for key, val in data.items():
            decoded_data[json.loads(key, cls=_Decoder)] = json.loads(val, cls=_Decoder)

        return decoded_data

    async def _hdel_data(self: 'Self', key: str, user_id: int) -> None:
        """Delete hash type of the data from the database."""
        await self.redis_cli.hdel(key, str(user_id))

    async def _hgetall_data(self: 'Self', key: str) -> dict[bytes, bytes]:
        """Return hash type of the data from the database."""
        return await self.redis_cli.hgetall(key)

    async def _hset_data(self: 'Self', key: str, user_id: int, data: 'UD') -> None:
        """Store the data to the database in the hash format under the specified key."""
        await self.redis_cli.hset(key, str(user_id), json.dumps(data, cls=_Encoder))

    async def _hsetall_data(self: 'Self', key: str, data: dict[int, 'UD']) -> None:
        """Replace hash type of the data to specified value."""
        async with self.redis_cli.pipeline() as pipe:
            pipe.multi()
            for field, value in data.items():
                await pipe.hset(key, str(field), json.dumps(value, cls=_Encoder))

            await pipe.execute()

    async def _set_data(self: 'Self', key: str, data: object) -> None:
        """Store the data to the database using the specified key."""
        await self.redis_cli.set(key, pickle.dumps(data))

    #
    # Public methods
    #

    async def drop_chat_data(self: 'Self', chat_id: int) -> None:
        """Delete the specified key from `chat_data` and, depending on
        the on_flush attribute, reflect the change in the database.
        """
        if self.chat_data is None:
            return

        with contextlib.suppress(KeyError):
            self.chat_data.pop(chat_id)


        if not self.on_flush:
            await self._set_data(self._CHAT_DATA_KEY, self.chat_data)

    async def drop_user_data(self: 'Self', user_id: int) -> None:
        """Delete the specified key from `user_data` and, depending on
        the on_flush attribute, reflect the change in the database.
        """
        if self.user_data is None:
            return

        self.user_data.pop(user_id, None)
        if not self.on_flush:
            await self._hdel_data(self._USER_DATA_KEY, user_id)

    async def flush(self: 'Self') -> None:
        """Store all the data kept in the memory to the database."""
        if self.bot_data:
            await self._set_data(self._BOT_DATA_KEY, self.bot_data)

        if self.callback_data:
            await self._set_data(self._CALLBACK_DATA_KEY, self.callback_data)

        if self.chat_data:
            await self._set_data(self._CHAT_DATA_KEY, self.chat_data)

        if self.conversations:
            await self._set_data(self._CONVERSATIONS_KEY, self.conversations)

        if self.user_data:
            await self._hsetall_data(self._USER_DATA_KEY, self.user_data)

    async def get_bot_data(self: 'Self') -> 'BD':
        """Return the bot data from the database, if it exists,
        or an empty object of the type `telegram.ext.ContextTypes.bot_data`
        otherwise.
        """
        if not self.bot_data:
            data = await self._get_data(self._BOT_DATA_KEY) or self.context_types.bot_data()

            self.bot_data = data

        return self.bot_data

    async def get_callback_data(self: 'Self') -> 'CDCData | None':
        """Return the callback data from the database, if it exists,
        or None otherwise.
        """
        if not self.callback_data:
            data = await self._get_data(self._CALLBACK_DATA_KEY)
            if not data:
                data = None

            self.callback_data = data

        if self.callback_data is None:
            return None

        return self.callback_data[0], self.callback_data[1].copy()

    async def get_chat_data(self: 'Self') -> 'defaultdict[int, CD]':
        """Return the chat data from the database, if it exists,
        or an empty dict otherwise.
        """
        if not self.chat_data:
            data = (await self._get_data(self._CHAT_DATA_KEY) or
                    defaultdict(self.context_types.chat_data))
            data = defaultdict(self.context_types.chat_data, data)

            self.chat_data = data

        return self.chat_data

    async def get_conversations(self: 'Self', name: str) -> 'ConversationDict':
        """Return the conversations from the database, if it exists,
        or an empty dict otherwise.
        """
        if not self.conversations:
            self.conversations = await self._get_data(self._CONVERSATIONS_KEY) or {name: {}}

        return self.conversations.get(name, {}).copy()

    async def get_user_data(self: 'Self') -> dict[int, 'UD']:
        """Return the user data from the database, if it exists,
        or an empty dict otherwise.
        """
        if not self.user_data:
            data = await self._hgetall_data(self._USER_DATA_KEY)
            self.user_data = self._decode_data(data)

        return self.user_data

    async def update_bot_data(self: 'Self', data: 'BD') -> None:
        """Update the bot data (if changed) and, depending on on_flush attribute,
        reflect the change in the database.
        """
        if self.bot_data == data:
            return

        self.bot_data = data
        if not self.on_flush:
            await self._set_data(self._BOT_DATA_KEY, self.bot_data)

    async def update_callback_data(self: 'Self', data: 'CDCData') -> None:
        """Update the callback data (if changed) and, depending on on_flush attribute,
        reflect the change in the database.
        """
        if self.callback_data == data:
            return

        self.callback_data = (data[0], data[1].copy())
        if not self.on_flush:
            await self._set_data(self._CALLBACK_DATA_KEY, self.callback_data)

    async def update_chat_data(self: 'Self', chat_id: int, data: 'CD') -> None:
        """Update the chat data (if changed) and, depending on on_flush attribute,
        reflect the change in the database.
        """
        if self.chat_data is None:
            self.chat_data = defaultdict(self.context_types.chat_data)

        if self.chat_data.get(chat_id) == data:
            return

        self.chat_data[chat_id] = data
        if not self.on_flush:
            await self._set_data(self._CHAT_DATA_KEY, self.chat_data)

    async def update_conversation(
        self: 'Self',
        name: str,
        key: 'ConversationKey',
        new_state: object | None,
    ) -> None:
        """Update the conversations for the given handler and, depending on on_flush attribute,
        reflect the change in the database.
        """
        if not self.conversations:
            self.conversations = {}

        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return

        self.conversations[name][key] = new_state
        if not self.on_flush:
            await self._set_data(self._CONVERSATIONS_KEY, self.conversations)

    async def update_user_data(self: 'Self', user_id: int, data: 'UD') -> None:
        """Update the user data (if changed) and, depending on the on_flush attribute,
        reflect the change in the database.
        """
        if self.user_data is None:
            self.user_data = {}

        if self.user_data.get(user_id) == data:
            return

        self.user_data[user_id] = data
        if not self.on_flush:
            await self._hset_data(self._USER_DATA_KEY, user_id, data)

    async def refresh_bot_data(self: 'Self', bot_data: 'BD') -> None:
        """Do nothing. Required by the `BasePersistence` interface."""

    async def refresh_chat_data(self: 'Self', chat_id: int, chat_data: 'CD') -> None:
        """Do nothing. Required by the `BasePersistence` interface."""

    async def refresh_user_data(self: 'Self', user_id: int, user_data: 'UD') -> None:
        """Do nothing. Required by the `BasePersistence` interface."""

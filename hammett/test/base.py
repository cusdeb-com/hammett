# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The module contains the base class for the tests for
both Hammett itself and the bots based on the framework.
"""

import asyncio
import difflib
import pprint
import unittest
from dataclasses import asdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from unittest.util import _common_shorten_repr

from asgiref.sync import async_to_sync
from telegram import Bot, Chat, Message, Update, User
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.constants import ChatType
from telegram.ext import Application, ApplicationBuilder, CallbackContext

from hammett.conf import settings
from hammett.core.constants import FinalRenderConfig, RenderConfig

if TYPE_CHECKING:
    from typing import Self

    from telegram._utils.types import JSONDict, ODVInput


class TestBot(Bot):
    """Class that represents a bot for testing purposes."""

    async def _do_post(
        self: 'Self',
        endpoint: str,  # noqa: ARG002
        data: 'JSONDict',  # noqa: ARG002
        *,
        read_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        write_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        connect_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        pool_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
    ) -> 'bool | JSONDict | list[JSONDict]':
        """Override the method not to send any request.

        Returns:
            Mock of sending request.

        """
        return {
            'message_id': 1,
            'from_user': 1,
            'chat': {
                'id': 1,
                'type': ChatType.PRIVATE,
            },
            'date': datetime.now(UTC).timestamp(),
        }


class BaseTestCase(unittest.TestCase):
    """The class that subclasses unittest.TestCase to make it
    familiar with the specifics of the framework.
    """

    update: 'Update'
    context: 'CallbackContext'  # type: ignore[type-arg]

    chat_id = 1
    message_id = 1
    update_id = 1
    user_id = 1

    def __init__(self: 'Self', method_name: str) -> None:
        """Initialize a base test case object."""
        self.chat = self.get_chat()
        self.context = self.get_context()
        self.user = self.get_user()
        self.message = self.get_message()
        self.update = self.get_update()

        super().__init__(method_name)

    def __call__(self: 'Self', result: 'unittest.result.TestResult | None' = None) -> None:
        """Override __call__ to wrap asynchronous tests."""
        test_method = getattr(self, self._testMethodName)
        if asyncio.iscoroutinefunction(test_method):
            setattr(self, self._testMethodName, async_to_sync(test_method))

        super().__call__(result)

    def get_chat(self) -> 'Chat':
        """Return the `Chat` object for testing purposes.

        Returns:
            `Chat` object.

        """
        return Chat(self.chat_id, ChatType.PRIVATE)

    def get_context(self) -> 'CallbackContext':  # type: ignore[type-arg]
        """Return the `CallbackContext` object for testing purposes.

        Returns:
            `CallbackContext` object.

        """
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
            user_id=self.user_id,
        )

    def get_message(self) -> 'Message':
        """Return the `Message` object for testing purposes.

        Returns:
            `Message` object.

        """
        return Message(
            self.message_id,
            datetime.now(tz=UTC),
            self.chat,
            from_user=self.user,
        )

    def get_native_application(self) -> 'Application':  # type: ignore[type-arg]
        """Return the `Application` object for testing purposes.

        Returns:
            `Application` object.

        """
        return (
            ApplicationBuilder()
            .bot(
                TestBot(token=settings.TOKEN),
            )
            .concurrent_updates(
                concurrent_updates=False,
            )
            .application_class(Application)
            .build()
        )

    def get_update(self) -> 'Update':
        """Return the `Update` object for testing purposes.

        Returns:
            `Update` object.

        """
        return Update(self.update_id, message=self.message)

    def get_user(self) -> 'User':
        """Return the `User` object for testing purposes.

        Returns:
            `User` object.

        """
        return User(self.user_id, 'TestUser', is_bot=False)

    def prepare_final_render_config(
        self,
        config: 'RenderConfig | FinalRenderConfig',
    ) -> 'FinalRenderConfig':
        """Transform `FinalRenderConfig` from `RenderConfig` if `RenderConfig` is provided,
        and pass the chat id to `FinalRenderConfig` for future assertions in tests.

        Returns:
            Ready `FinalRenderConfig` object.

        """
        if not isinstance(config, FinalRenderConfig):
            # The default keyboard needs to be replaced when casting to FinalRenderConfig.
            if config.keyboard is None:
                config.keyboard = []

            config = FinalRenderConfig(**asdict(config))

        config.chat_id = self.chat.id
        return config

    def assertFinalRenderConfigEqual(  # noqa: N802
        self,
        expected: 'FinalRenderConfig',
        actual: 'FinalRenderConfig',
        msg: str | None = None,
    ) -> None:
        """Compare two FinalRenderConfig objects."""
        assert isinstance(expected, FinalRenderConfig), 'First argument is not a FinalRenderConfig'  # noqa: S101
        assert isinstance(actual, FinalRenderConfig), 'Second argument is not a FinalRenderConfig'  # noqa: S101

        if expected != actual:
            first_config_repr, second_config_repr = _common_shorten_repr(
                expected,  # type: ignore[arg-type]
                actual,  # type: ignore[arg-type]
            )

            standard_msg = f'{first_config_repr} != {second_config_repr}'
            diff = '\n' + '\n'.join(
                difflib.ndiff(
                    pprint.pformat(expected).splitlines(),
                    pprint.pformat(actual).splitlines(),
                ),
            )

            standard_msg = self._truncateMessage(standard_msg, diff)  # type: ignore[attr-defined]

            self.fail(self._formatMessage(msg, standard_msg))

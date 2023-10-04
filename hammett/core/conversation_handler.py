# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2023
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""The module contains a modified version of the ConversationHandler class,
optimized for debugging purposes.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

from telegram._utils.defaultvalue import DefaultValue
from telegram._utils.warnings import warn
from telegram.ext import ConversationHandler as NativeConversationHandler
from telegram.ext._application import ApplicationHandlerStop
from telegram.ext._extbot import ExtBot

if TYPE_CHECKING:
    from typing import Any

    from telegram import Update
    from telegram.ext import Application
    from telegram.ext._utils.types import CCT
    from typing_extensions import Self

    from hammett.types import CheckUpdateType

DEFAULT_TRUE: DefaultValue[bool] = DefaultValue(value=True)

LOGGER = logging.getLogger(__name__)


class ConversationHandler(NativeConversationHandler['Any']):
    """The class that subclasses `telegram.ext.ConversationHandler` to
    enable logging of state transitions in debug mode.
    """

    async def handle_update(  # type: ignore[override]  # noqa:C901, PLR0912
        self: 'Self',
        update: 'Update',
        application: 'Application[Any, CCT, Any, Any, Any, Any]',
        check_result: 'CheckUpdateType[CCT]',
        context: 'CCT',
    ) -> object | None:
        """Send the update to the callback for the current state and BaseHandler."""

        current_state, conversation_key, handler, handler_check_result = check_result
        raise_dp_handler_stop = False

        async with self._timeout_jobs_lock:
            # Remove the old timeout job (if present)
            timeout_job = self.timeout_jobs.pop(conversation_key, None)

            if timeout_job is not None:
                timeout_job.schedule_removal()

        # Resolution order of "block":
        # 1. Setting of the selected handler
        # 2. Setting of the ConversationHandler
        # 3. Default values of the bot
        if handler.block is not DEFAULT_TRUE:
            block = handler.block
        elif self._block is not DEFAULT_TRUE:
            block = self._block
        elif isinstance(application.bot, ExtBot) and application.bot.defaults is not None:
            block = application.bot.defaults.block
        else:
            block = DefaultValue.get_value(handler.block)

        try:  # Now create task or await the callback
            if block:
                new_state: object = await handler.handle_update(
                    update, application, handler_check_result, context,
                )
            else:
                new_state = application.create_task(
                    coroutine=handler.handle_update(
                        update, application, handler_check_result, context,
                    ),
                    update=update,
                )
        except ApplicationHandlerStop as exception:
            new_state = exception.state
            raise_dp_handler_stop = True
        async with self._timeout_jobs_lock:
            if self.conversation_timeout:
                if application.job_queue is None:
                    warn(
                        'Ignoring `conversation_timeout` because the Application has no JobQueue.',
                        stacklevel=1,
                    )
                elif not application.job_queue.scheduler.running:
                    warn(
                        'Ignoring `conversation_timeout` because the Applications JobQueue is '
                        'not running.',
                        stacklevel=1,
                    )
                elif isinstance(new_state, asyncio.Task):
                    # Add the new timeout job
                    # checking if the new state is self.END is done in _schedule_job
                    application.create_task(
                        self._schedule_job_delayed(
                            new_state, application, update, context, conversation_key,
                        ),
                        update=update,
                    )
                else:
                    self._schedule_job(new_state, application, update, context, conversation_key)

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self._update_state(self.END, conversation_key, handler)
            if raise_dp_handler_stop:
                raise ApplicationHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        if current_state != self.WAITING:
            self._update_state(new_state, conversation_key, handler)

            try:
                handler_name = (
                    f'{type(handler.callback.__self__).__name__}.'  # type: ignore[attr-defined]
                    f'{handler.callback.__name__}'
                )
            except AttributeError:
                handler_name = f'{handler.callback.__qualname__}'

            if current_state != new_state:
                msg = (
                    f'Switched to `{new_state}` state from '
                    f'`{current_state}` state via `{handler_name}` handler.'
                )
                LOGGER.debug(msg)

        if raise_dp_handler_stop:
            # Don't pass the new state here. If we're in a nested conversation, the parent is
            # expecting None as return value.
            raise ApplicationHandlerStop
        # Signals a possible parent conversation to stay in the current state
        return None

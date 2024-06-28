"""The module contains helpers for working with RenderConfig."""

import logging
from typing import TYPE_CHECKING, cast

from hammett.core.constants import LATEST_SENT_MSG_KEY
from hammett.core.exceptions import MissingPersistence

if TYPE_CHECKING:
    from telegram import Message
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.core.constants import FinalRenderConfig, LatestMsg

LOGGER = logging.getLogger(__name__)


def get_latest_msg(
    context: 'CallbackContext[BT, UD, CD, BD]',
    message: 'Message',
) -> 'LatestMsg | None':
    """Return the latest sent message info."""
    state: LatestMsg | None = None
    try:
        state = context.user_data[LATEST_SENT_MSG_KEY]  # type: ignore[index]
    except KeyError:
        pass
    except TypeError:
        if context._application.persistence:  # noqa: SLF001
            try:
                user_data = cast('UD', {**context._application.user_data})  # noqa: SLF001
                state = user_data[message.chat_id][LATEST_SENT_MSG_KEY]  # type: ignore[index]
            except KeyError:
                pass

    return state


async def save_latest_msg(
    context: 'CallbackContext[BT, UD, CD, BD]',
    config: 'FinalRenderConfig',
    message: 'Message',
) -> None:
    """Save the latest message info."""
    latest_msg = {
        'hide_keyboard': config.hide_keyboard,
        'message_id': message.message_id,
        'chat_id': message.chat_id,
    }
    try:
        context.user_data[LATEST_SENT_MSG_KEY] = latest_msg  # type: ignore[index]
    except TypeError as exc:
        if not context._application.persistence:  # noqa: SLF001
            msg = (
                "It's not possible to pass data to user_data. "
                f"To solve the issue either don't use {save_latest_msg.__name__} in jobs "
                f"or configure persistence."
            )
            raise MissingPersistence(msg) from exc

        user_data = cast('UD', {**context._application.user_data})  # noqa: SLF001
        try:
            user_data[message.chat_id].update({  # type: ignore[index]
                LATEST_SENT_MSG_KEY: latest_msg,
            })
        except KeyError:
            msg = f'Can not update user_data with the message id ({message.id})'
            LOGGER.warning(msg)

        await context._application.persistence.update_user_data(  # noqa: SLF001
            message.chat_id,
            user_data,
        )

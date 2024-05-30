"""The module contains helpers for working with RenderConfig."""

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, cast

from hammett.core.constants import LATEST_SENT_MSG_KEY
from hammett.core.exceptions import MissingPersistence

if TYPE_CHECKING:
    from telegram import Message
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.core.constants import FinalRenderConfig, SerializedFinalRenderConfig

LOGGER = logging.getLogger(__name__)


async def get_latest_msg_config(
    context: 'CallbackContext[BT, UD, CD, BD]',
    message: 'Message',
) -> 'SerializedFinalRenderConfig | None':
    """Return the latest sent saved render config."""
    state: 'SerializedFinalRenderConfig | None' = None
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


async def save_latest_msg_config(
    context: 'CallbackContext[BT, UD, CD, BD]',
    config: 'FinalRenderConfig',
    message: 'Message',
) -> None:
    """Save the latest render config."""
    latest_msg = {
        **asdict(config),
        'message_id': message.message_id,
    }
    try:
        context.user_data[LATEST_SENT_MSG_KEY] = latest_msg  # type: ignore[index]
    except TypeError as exc:
        if not context._application.persistence:  # noqa: SLF001
            msg = (
                "It's not possible to pass data to user_data. "
                f"To solve the issue either don't use {save_latest_msg_config.__name__} in jobs "
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

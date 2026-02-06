"""The module contains helpers for working with RenderConfig."""

from typing import TYPE_CHECKING

from hammett.core.constants import LATEST_SENT_MSG_KEY
from hammett.core.exceptions import MissingPersistenceError

if TYPE_CHECKING:
    from telegram import Message
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.core.constants import FinalRenderConfig, LatestMessage


def get_latest_message(
    context: 'CallbackContext[BT, UD, CD, BD]',
    message: 'Message',
) -> 'LatestMessage | None':
    """Return the latest sent message info.

    Returns:
        Latest sent message info.

    """
    state: LatestMessage | None = None
    try:
        state = context.user_data[LATEST_SENT_MSG_KEY]  # type: ignore[index]
    except KeyError:
        pass
    except TypeError:
        if context._application.persistence:  # noqa: SLF001
            try:
                user_data = context._application.user_data[message.chat_id]  # noqa: SLF001
                state = user_data[LATEST_SENT_MSG_KEY]  # type: ignore[index]
            except KeyError:
                pass

    return state


async def save_latest_message(
    context: 'CallbackContext[BT, UD, CD, BD]',
    config: 'FinalRenderConfig',
    message: 'Message',
) -> None:
    """Save the latest message info.

    Raises:
        MissingPersistenceError: If the attempt to save the latest message information fails because
        the message was sent via a job.

    """
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
                f"To solve the issue either don't use {save_latest_message.__name__} in jobs "
                f'or configure persistence.'
            )
            raise MissingPersistenceError(msg) from exc

        user_data = context._application.user_data[message.chat_id]  # noqa: SLF001
        user_data.update(  # type: ignore[attr-defined]
            {
                LATEST_SENT_MSG_KEY: latest_msg,
            },
        )

        await context._application.persistence.update_user_data(  # noqa: SLF001
            message.chat_id,
            user_data,
        )

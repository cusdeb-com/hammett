"""The module contains an error handler with managed logic of logging."""

# ruff: noqa: RUF029, PLR0916

import logging
from typing import TYPE_CHECKING

from telegram.error import BadRequest, TimedOut

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

_QUERY_IS_TOO_OLD = 'Query is too old and response timeout expired or query id is invalid'

_TIMED_OUT = 'Timed out'

_UPDATE_MASSAGE_FAIL = 'Message is not modified'

LOGGER = logging.getLogger(__name__)


async def default_error_handler(
    _update: 'Update',
    context: 'CallbackContext[BT, UD, CD, BD]',
) -> None:
    """Log some of the Telegram exceptions depending on the settings."""
    from hammett.conf import settings

    error = context.error
    if (
        hasattr(error, 'message')
        and isinstance(error, BadRequest | TimedOut)
        and (
            (
                settings.ERROR_HANDLER_CONF.get('IGNORE_QUERY_IS_TOO_OLD')
                and error.message == _QUERY_IS_TOO_OLD
            )
            or (settings.ERROR_HANDLER_CONF.get('IGNORE_TIMED_OUT') and error.message == _TIMED_OUT)
            or (
                settings.ERROR_HANDLER_CONF.get('IGNORE_UPDATE_MASSAGE_FAIL')
                and error.message.startswith(_UPDATE_MASSAGE_FAIL)
            )
        )
    ):
        LOGGER.warning(error.message)
    else:
        raise error  # type: ignore[misc]

"""The module contains error handlers for the demo."""

# ruff: noqa: I001

import logging

from telegram.ext import ApplicationHandlerStop

from exeptions import CustomError

LOGGER = logging.getLogger(__name__)


async def custom_error_handler(update, context):
    """Receive every error which happens in the bot and process the `CustomError` exception."""
    if update:
        query = update.callback_query
        if query:
            await query.answer('Request failed')
    else:
        LOGGER.warning('Exception without update object: %s', context.error)

    # This check is needed to interrupt the sequence of calls
    # registered error handlers.
    if isinstance(context.error, CustomError):
        LOGGER.warning('CustomError intercepted — stopping further error handlers')
        raise ApplicationHandlerStop

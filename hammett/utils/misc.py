"""The module contains various helper procedures used in hammett."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import CallbackQuery, Update


async def get_callback_query(update: 'Update') -> 'CallbackQuery | None':
    """Get CallbackQuery from Update."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed.
    # Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    if query:
        await query.answer()

    return query

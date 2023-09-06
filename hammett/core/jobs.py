"""The module contains the base class for all custom notification screens."""

from typing import TYPE_CHECKING

from telegram.constants import ParseMode

from hammett.core.screen import Screen

if TYPE_CHECKING:
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Keyboard


class BaseNotification(Screen):
    """The base class for implementing custom notification screens."""

    async def send(
        self: 'Self',
        chat_id: int,
        keyboard: 'Keyboard',
        context: 'CallbackContext[BT, UD, CD, BD]',
        text: str = '',
        image: 'str | None' = None,
    ) -> None:
        """Sends the screen to the specified chat."""

        update = None  # a job handler doesn't accept an Update object
        if image:
            await context.bot.send_photo(
                caption=text,
                chat_id=chat_id,
                photo=image,
                parse_mode=ParseMode.HTML,
                reply_markup=await self._create_markup_keyboard(keyboard, update, context),
            )
        else:
            await context.bot.send_message(
                text=text,
                chat_id=chat_id,
                parse_mode=ParseMode.HTML,
                reply_markup=await self._create_markup_keyboard(keyboard, update, context),
            )

"""The module contains the implementation of the multi choice widget."""

from typing import TYPE_CHECKING

from hammett.widgets.base import BaseChoiceWidget

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.widgets.types import WidgetState


class MultiChoiceWidget(BaseChoiceWidget):
    """The class implements the multi choice widget."""

    chosen_emoji = '✅'
    unchosen_emoji = '🔲'

    async def get_chosen_choices(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'WidgetState':
        """Returns the choices made by the user."""

        return await self.get_state(update, context)

    async def switch(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        choice: tuple[str, str],
        choices: 'WidgetState',
    ) -> None:
        """Switches the widget from one state to another."""

        if choice in choices:
            choices.remove(choice)
        else:
            choices.append(choice)

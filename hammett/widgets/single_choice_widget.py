"""The module contains the implementation of the single choice widget."""

import logging
from contextlib import suppress
from typing import TYPE_CHECKING

from hammett.widgets.base import BaseChoiceWidget

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.widgets.types import WidgetState

LOGGER = logging.getLogger(__name__)


class SingleChoiceWidget(BaseChoiceWidget):
    """The class implements the single choice widget."""

    chosen_emoji = '🔘'
    initial_value: str | None = None
    unchosen_emoji = '◯'

    #
    # Private methods
    #

    async def _initialize_choices(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Initialize choices."""

        initial_value = await self.get_initial_value(update, context)
        if initial_value is not None:
            found_choice = None
            for choice in await self.get_choices(update, context):
                with suppress(StopIteration):
                    next(filter(lambda x: x == initial_value, choice))
                    found_choice = [choice]
                    break

            if found_choice is None:
                msg = 'No matches with initial_value'
                LOGGER.warning(msg)

            await self._set_state(update, context, found_choice)

    #
    # Public methods
    #

    async def get_chosen_choice(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'WidgetState':
        """Returns the choice made by the user."""

        return await self.get_state(update, context)

    async def get_initial_value(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str | None:
        """Returns the `initial_value` attribute of the widget."""

        return self.initial_value

    async def switch(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        choice: tuple[str, str],
        choices: 'WidgetState',
    ) -> None:
        """Switches the widget from one state to another."""

        with suppress(IndexError):
            choices.pop()

        choices.append(choice)

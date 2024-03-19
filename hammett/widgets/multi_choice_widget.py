"""The module contains the implementation of the multi choice widget."""

import logging
from contextlib import suppress
from typing import TYPE_CHECKING

from hammett.widgets.base import BaseChoiceWidget

if TYPE_CHECKING:
    from collections.abc import Sequence

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.widgets.types import WidgetState

LOGGER = logging.getLogger(__name__)


class MultiChoiceWidget(BaseChoiceWidget):
    """The class implements the multi choice widget."""

    chosen_emoji = '✅'
    initial_values: 'Sequence[str] | None' = None
    unchosen_emoji = '🔲'

    #
    # Private methods
    #

    async def _initialize_choices(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Initialize the choices."""

        initial_values = await self.get_initial_values(update, context)
        if initial_values is not None:
            found_choices = []
            for choice in await self.get_choices(update, context):
                for initial_value in initial_values:
                    with suppress(StopIteration):
                        next(filter(lambda x: initial_value in x, choice))
                        found_choices.append(choice)
                        continue

            if not found_choices:
                msg = 'No matches with initial_values'
                LOGGER.warning(msg)

            await self._set_state(update, context, found_choices)


    #
    # Public methods
    #

    async def get_chosen_choices(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'WidgetState':
        """Returns the choices made by the user."""

        return await self.get_state(update, context)

    async def get_initial_values(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Sequence[str] | None':
        """Returns the `initial_values` attribute of the widget."""

        return self.initial_values

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

"""The module contains the implementation of the multi choice widget."""

from typing import TYPE_CHECKING

from hammett.widgets.base import BaseChoiceWidget

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.widgets.types import Choice, Choices, InitializedChoices


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
        choices: 'Choices',
        **_kwargs: 'Any',
    ) -> 'InitializedChoices':
        """Initialize choices."""

        initial_values = await self.get_initial_values(update, context)
        if initial_values is not None:
            initialized_choices = [
                (choice_key in initial_values, choice_key, choice_value)
                for choice_key, choice_value in choices
            ]
        else:
            initialized_choices = [
                (False, choice_key, choice_value)
                for choice_key, choice_value in choices
            ]

        return tuple(initialized_choices)

    #
    # Public methods
    #

    async def get_initial_values(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Sequence[str] | None':
        """Returns the `initial_values` attribute of the widget."""

        return self.initial_values

    async def switch(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        selected_choice: 'Choice',
    ) -> 'InitializedChoices':
        """Switches the widget from one state to another."""

        current_choices = await self.get_initialized_choices(update, context)

        choices = []
        for is_chosen, choice_key, choice_value in current_choices:
            chosen = is_chosen
            if choice_key == selected_choice[0]:
                chosen = not is_chosen

            choices.append((chosen, choice_key, choice_value))

        return tuple(choices)

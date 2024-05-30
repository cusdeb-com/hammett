"""The module contains the implementation of the single choice widget."""

from typing import TYPE_CHECKING

from hammett.widgets.base import BaseChoiceWidget

if TYPE_CHECKING:
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.widgets.types import Choice, Choices, InitializedChoices


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
        choices: 'Choices',
        **_kwargs: 'Any',
    ) -> 'InitializedChoices':
        """Initialize choices."""
        initial_value = await self.get_initial_value(update, context)
        if initial_value is not None:
            initialized_choices = [
                (choice_key == initial_value, choice_key, choice_value)
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

    async def get_initial_value(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str | None:
        """Return the `initial_value` attribute of the widget."""
        return self.initial_value

    async def switch(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        selected_choice: 'Choice',
    ) -> 'InitializedChoices':
        """Switch the widget from one state to another."""
        current_choices = await self.get_initialized_choices(update, context)

        return tuple([
            (choice_key == selected_choice[0], choice_key, choice_value)
            for _, choice_key, choice_value in current_choices
        ])

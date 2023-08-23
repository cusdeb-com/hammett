"""The module contains base classes for widgets from the library."""

import json
from typing import TYPE_CHECKING, Any, cast

from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.core.screen import Button, RenderConfig, Screen
from hammett.widgets.exceptions import (
    ChoiceEmojisAreUndefined,
    ChoicesFormatIsInvalid,
    FailedToGetStateKey,
    NoChoicesSpecified,
)

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Keyboard, Stage
    from hammett.widgets.types import Choices, WidgetState


class BaseWidget(Screen):
    """The class implements the base interface for widgets from the library."""

    async def _get_state_key(self: 'Self', update: 'Update') -> str:
        """Returns a widget state."""

        query = await self.get_callback_query(update)
        message = getattr(query, 'message', None)
        if message is None:
            raise FailedToGetStateKey

        return f'{self.__class__.__name__}_{message.chat_id}_{message.message_id}'

    async def get_state(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'WidgetState':
        """Returns the widget state."""

        state_key = await self._get_state_key(update)
        user_data = cast('dict[str, Any]', context.user_data)
        try:
            state = user_data[state_key]
        except KeyError:
            user_data[state_key] = []
            state = user_data[state_key]

        return cast('WidgetState', state)


class BaseChoiceWidget(BaseWidget):
    """The class implements the base interface for the choice widgets."""

    choices: 'Choices' = ()
    chosen_emoji: str = ''
    unchosen_emoji: str = ''

    def __init__(self: 'Self') -> None:
        super().__init__()

        if not isinstance(self.choices, tuple):
            msg = f'The choices attribute of {self.__class__.__name__} must be a tuple of tuples'
            raise ChoicesFormatIsInvalid(msg)

        if not len(self.choices):
            msg = f'{self.__class__.__name__} must specify at least one choice'
            raise NoChoicesSpecified(msg)

        if self.chosen_emoji == '' or self.unchosen_emoji == '':
            msg = f'{self.__class__.__name__} must specify both chosen_emoji and unchosen_emoji'
            raise ChoiceEmojisAreUndefined(msg)

    #
    # Private methods
    #

    def _build_keyboard(
        self: 'Self',
        choices: 'WidgetState | None' = None,
    ) -> 'Keyboard':
        """Builds the keyboard based on the specified choices."""

        if choices is None:
            choices = []

        keyboard = []
        for choice in self.choices:
            try:
                code, name = choice
            except (TypeError, ValueError) as exc:
                msg = (
                    f'Each choice of {self.__class__.__name__} must be '
                    f'a tuple containing a code and a name'
                )
                raise ChoicesFormatIsInvalid(msg) from exc

            box = self.chosen_emoji if choice in choices else self.unchosen_emoji
            keyboard.append([
                Button(
                    f'{box} {name}',
                    self._on_choice_click,  # type: ignore[arg-type]
                    payload=json.dumps({'code': code, 'name': name}),
                    source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                ),
            ])

        return keyboard + self.add_extra_keyboard()

    async def _on_choice_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Invoked when clicking on a choice."""

        choices = await self.get_state(update, context)
        payload: dict[str, str] = json.loads(await self.get_payload(update, context))

        await self.switch((payload['code'], payload['name']), choices)
        keyboard = self._build_keyboard(choices)
        config = RenderConfig(
            keyboard=keyboard,
        )
        await self.render(update, context, config=config)
        return DEFAULT_STAGE

    #
    # Public methods
    #

    def add_extra_keyboard(self: 'Self') -> 'Keyboard':
        """Adds an extra keyboard below the choice buttons."""

        return []

    async def render(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
    ) -> None:
        """Overrides the render method to build the keyboard based on
        the specified choices before rendering the widget.
        """

        if config is None:
            config = RenderConfig(keyboard=self._build_keyboard())

        await super().render(update, context, config=config)

    def setup_keyboard(self: 'Self') -> 'Keyboard':
        """Registers the widget handlers."""

        return [
            [
                Button(
                    'ok',
                    self._on_choice_click,  # type: ignore[arg-type]
                    source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                ),
            ],
            *self.add_extra_keyboard(),
        ]

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Handles the /start command when the widget is used as a start screen."""

        await self.render(update, context, config=RenderConfig(as_new_message=True))
        return DEFAULT_STAGE

    async def switch(
        self: 'Self',
        choice: tuple[str, str],
        choices: 'WidgetState',
    ) -> None:
        """Switches the widget from one state to another."""

        raise NotImplementedError

"""The module contains base classes for widgets from the library."""

import json
from typing import TYPE_CHECKING, Any, cast

from hammett.core import Button, Screen
from hammett.core.constants import DEFAULT_STATE, EMPTY_KEYBOARD, RenderConfig, SourcesTypes
from hammett.core.handlers import register_button_handler
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

    from hammett.types import Keyboard, State
    from hammett.widgets.types import Choices, WidgetState


class BaseWidget(Screen):
    """The class implements the base interface for widgets from the library."""

    async def _get_state_key(
        self: 'Self',
        update: 'Update | None' = None,
        chat_id: int = 0,
        message_id: int = 0,
    ) -> str:
        """Returns a widget state key."""

        if update:
            query = await self.get_callback_query(update)
            message = getattr(query, 'message', None)
            if message is None:
                raise FailedToGetStateKey

            current_chat_id = message.chat_id
            current_message_id = message.message_id
        else:
            current_chat_id = chat_id
            current_message_id = message_id

        return f'{self.__class__.__name__}_{current_chat_id}_{current_message_id}'

    async def add_extra_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Adds an extra keyboard below the widget buttons."""

        return EMPTY_KEYBOARD

    async def get_state(
        self: 'Self',
        update: 'Update | None',
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

        if self.chosen_emoji == '' or self.unchosen_emoji == '':
            msg = f'{self.__class__.__name__} must specify both chosen_emoji and unchosen_emoji'
            raise ChoiceEmojisAreUndefined(msg)

    #
    # Private methods
    #

    async def _build_keyboard(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        chosen: 'WidgetState',
    ) -> 'Keyboard':
        """Builds the keyboard based on the specified choices."""

        choices = await self.get_choices(update, context)
        if not isinstance(choices, tuple):
            msg = f'The choices attribute of {self.__class__.__name__} must be a tuple of tuples'
            raise ChoicesFormatIsInvalid(msg)

        if not len(choices):
            msg = f'{self.__class__.__name__} must specify at least one choice'
            raise NoChoicesSpecified(msg)

        keyboard = []
        for choice in choices:
            try:
                code, name = choice
            except (TypeError, ValueError) as exc:
                msg = (
                    f'Each choice of {self.__class__.__name__} must be '
                    f'a tuple containing a code and a name'
                )
                raise ChoicesFormatIsInvalid(msg) from exc

            box = self.chosen_emoji if choice in chosen else self.unchosen_emoji
            keyboard.append([
                Button(
                    f'{box} {name}',
                    self._on_choice_click,
                    payload=json.dumps({'code': code, 'name': name}),
                    source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                ),
            ])

        return keyboard + await self.add_extra_keyboard(update, context)

    @register_button_handler
    async def _on_choice_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *_args: 'Any',
        **_kwargs: 'Any',
    ) -> 'State':
        """Invoked when clicking on a choice."""

        choices = await self.get_state(update, context)
        payload: dict[str, str] = json.loads(await self.get_payload(update, context))

        await self.switch(update, context, (payload['code'], payload['name']), choices)
        keyboard = await self._build_keyboard(update, context, choices)
        config = RenderConfig(
            keyboard=keyboard,
        )
        await self.render(update, context, config=config)
        return DEFAULT_STATE

    #
    # Public methods
    #

    async def add_default_keyboard(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Sets up the default keyboard for the widget."""

        return await self._build_keyboard(
            update,
            context,
            await self.get_state(update, context),
        )

    async def get_choices(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Choices':
        """Returns the `choices` attribute of the widget."""

        return self.choices

    async def switch(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        choice: tuple[str, str],
        choices: 'WidgetState',
    ) -> None:
        """Switches the widget from one state to another."""

        raise NotImplementedError

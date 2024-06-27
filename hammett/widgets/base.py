"""The module contains base classes for widgets from the library."""

import contextlib
import json
import logging
import operator
from typing import TYPE_CHECKING, cast

import telegram

from hammett.core import Button, Screen
from hammett.core.constants import (
    DEFAULT_STATE,
    EMPTY_KEYBOARD,
    RenderConfig,
    SourcesTypes,
)
from hammett.core.exceptions import MissingPersistence
from hammett.core.handlers import register_button_handler
from hammett.utils.misc import get_callback_query
from hammett.widgets.exceptions import (
    ChoiceEmojisAreUndefined,
    ChoicesFormatIsInvalid,
    FailedToGetStateKey,
    NoChoicesSpecified,
)

if TYPE_CHECKING:
    from typing import Any

    from telegram import Message, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.constants import FinalRenderConfig
    from hammett.types import Keyboard, State
    from hammett.widgets.types import Choice, Choices, InitializedChoices

LOGGER = logging.getLogger(__name__)


class BaseWidget(Screen):
    """The class implements the base interface for widgets from the library."""

    async def _post_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        message: 'Message | tuple[Message]',
        config: 'FinalRenderConfig',
        **kwargs: 'Any',
    ) -> None:
        """Save to user_data initialized state after screen rendering if it's new message."""
        await super()._post_render(update, context, message, config, **kwargs)

        if isinstance(message, tuple):
            message = message[-1]

        if kwargs:
            state_key = await self._get_state_key(
                chat_id=message.chat_id,
                message_id=message.message_id,
            )
            try:
                context.user_data[state_key] = await self._initialized_state(  # type: ignore[index]
                    update,
                    context,
                    message,
                    config,
                    **kwargs,
                )
            except TypeError as exc:  # raised when messages are sent from jobs
                if not context._application.persistence:  # noqa: SLF001
                    msg = (
                        f"It's not possible to pass data to user_data. "
                        f"To solve the issue either don't use {self.__class__.__name__} in jobs "
                        f"or configure persistence."
                    )
                    raise MissingPersistence(msg) from exc
                user_data = cast('UD', {**context._application.user_data})  # noqa: SLF001
                try:
                    user_data[message.chat_id].update({  # type: ignore[index]
                        state_key: await self._initialized_state(
                            update,
                            context,
                            message,
                            config,
                            **kwargs,
                        ),
                    })
                except KeyError:
                    msg = (
                        f'Can not update user_data with the carousel widget message id '
                        f'({message.id})'
                    )
                    LOGGER.warning(msg)

                await context._application.persistence.update_user_data(  # noqa: SLF001
                    message.chat_id,
                    user_data,
                )

    async def _initialized_state(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _message: 'Message',
        _config: 'FinalRenderConfig',
        **_kwargs: 'Any',
    ) -> 'dict[Any, Any]':
        """Return the post-initialization widget state to be saved in context."""
        raise NotImplementedError

    async def _get_state_key(
        self: 'Self',
        update: 'Update | None' = None,
        chat_id: int = 0,
        message_id: int = 0,
    ) -> str:
        """Return a widget state key."""
        if update:
            query = await get_callback_query(update)
            message = getattr(query, 'message', None)
            if message is None:
                raise FailedToGetStateKey

            current_chat_id = message.chat_id
            current_message_id = message.message_id
        else:
            current_chat_id = chat_id
            current_message_id = message_id

        return f'{self.__class__.__name__}_{current_chat_id}_{current_message_id}'

    async def get_state_value(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        state_key: str,
    ) -> 'Any | None':
        """Safely get the specified value from the widget state dictionary
        stored in user_data.
        """
        state_value = None
        if context.user_data:
            user_data = cast('dict[str, Any]', context.user_data)
            try:
                current_state_key = await self._get_state_key(update)
                state = user_data.get(current_state_key)
            except FailedToGetStateKey:
                return None

            if state and state.get(state_key):
                state_value = state[state_key]

        return state_value

    async def set_state_value(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        state_key: str,
        state_value: 'Any',
    ) -> None:
        """Safely set the specified value to widget state dictionary
        stored in user_data.
        """
        if not context.user_data:
            return

        with contextlib.suppress(FailedToGetStateKey):  # raised when invoked on /start
            current_state_key = await self._get_state_key(update)
            user_data = cast('dict[str, Any]', context.user_data)

            current_state = user_data.get(current_state_key, {})
            current_state.update({
                state_key: state_value,
            })
            context.user_data[current_state_key] = current_state  # type: ignore[index]

    async def add_extra_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Add an extra keyboard below the widget buttons."""
        return EMPTY_KEYBOARD


class BaseChoiceWidget(BaseWidget):
    """The class implements the base interface for the choice widgets."""

    choices: 'Choices' = ()
    chosen_emoji: str = ''
    unchosen_emoji: str = ''

    def __init__(self: 'Self') -> None:
        """Initialize a base choice widget object."""
        super().__init__()

        if not self.chosen_emoji or not self.unchosen_emoji:
            msg = f'{self.__class__.__name__} must specify both chosen_emoji and unchosen_emoji'
            raise ChoiceEmojisAreUndefined(msg)

    #
    # Private methods
    #

    async def _initialize_choices(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        choices: 'Choices',
        **kwargs: 'Any',
    ) -> 'InitializedChoices':
        """Initialize choices."""
        raise NotImplementedError

    async def _initialized_state(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _message: 'Message',
        _config: 'FinalRenderConfig',
        choices: 'Choices | None' = None,
        **kwargs: 'Any',  # noqa: ARG002
    ) -> 'dict[Any, Any]':
        """Return the post-initialization widget state to be saved in context."""
        return {
            'choices': choices or (),
        }

    async def _build_keyboard(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        choices: 'InitializedChoices',
    ) -> 'Keyboard':
        """Build the keyboard based on the specified choices."""
        if not len(choices):
            msg = f'{self.__class__.__name__} must specify at least one choice'
            raise NoChoicesSpecified(msg)

        keyboard = []
        for choice in choices:
            try:
                chosen, code, name = choice
            except (TypeError, ValueError) as exc:
                msg = (
                    f'Each choice of {self.__class__.__name__} must be '
                    f'a tuple containing a code and a name'
                )
                raise ChoicesFormatIsInvalid(msg) from exc

            box = self.chosen_emoji if chosen else self.unchosen_emoji
            keyboard.append([
                Button(
                    f'{box} {name}',
                    self._on_choice_click,
                    payload=json.dumps({'code': code, 'name': name}),
                    source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                ),
            ])

        return keyboard + await self.add_extra_keyboard(update, context)

    async def _init(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None' = None,
        choices: 'Choices | None' = None,
        **kwargs: 'Any',
    ) -> 'State':
        """Initialize the widget."""
        current_choices = choices or await self.get_choices(update, context, **kwargs)
        initialized_choices = await self._initialize_choices(
            update,
            context,
            current_choices,
            **kwargs,
        )

        config = config or RenderConfig()
        config.keyboard = await self._build_keyboard(
            update,
            context,
            initialized_choices,
        )

        await self.render(
            update,
            context,
            config=config,
            choices=initialized_choices,
        )
        return DEFAULT_STATE

    @register_button_handler
    async def _on_choice_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *_args: 'Any',
        **_kwargs: 'Any',
    ) -> 'State':
        """Invoke when clicking on a choice."""
        payload: dict[str, str] = json.loads(await self.get_payload(update, context))

        choices = await self.switch(update, context, (payload['code'], payload['name']))
        keyboard = await self._build_keyboard(update, context, choices)
        config = RenderConfig(
            keyboard=keyboard,
        )

        await self.set_state_value(update, context, 'choices', choices)
        with contextlib.suppress(telegram.error.BadRequest):
            await self.render(update, context, config=config)

        return DEFAULT_STATE

    #
    # Public methods
    #

    async def get_choices(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'Choices':
        """Return the `choices` attribute of the widget."""
        return self.choices

    async def get_initialized_choices(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'InitializedChoices':
        """Return the initialized choices."""
        current_choices: InitializedChoices = await self.get_state_value(
            update,
            context,
            'choices',
        ) or ()

        return current_choices

    async def get_chosen_choices(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'InitializedChoices':
        """Return the choices made by the user."""
        current_choices = await self.get_initialized_choices(update, context)
        return tuple(filter(operator.itemgetter(0), current_choices))

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is used as StartScreen."""
        config = RenderConfig(as_new_message=True)
        return await self._init(update, context, config=config)

    async def move(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is passed to Button as `MOVE_SOURCE_TYPE`."""
        return await self._init(update, context)

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        choices: 'Choices | None' = None,
        **_kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is used as a notification."""
        config = config or RenderConfig()
        config.as_new_message = True

        return await self._init(None, context, config, choices=choices)

    async def switch(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        selected_choice: 'Choice',
    ) -> 'InitializedChoices':
        """Switch the widget from one state to another."""
        raise NotImplementedError

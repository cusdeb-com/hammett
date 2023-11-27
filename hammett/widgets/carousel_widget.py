"""The module contains the implementation of the carousel widget."""

import contextlib
from typing import TYPE_CHECKING, cast

from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.handlers import register_button_handler
from hammett.core.screen import Button, NotificationScreen, RenderConfig, StartScreen
from hammett.widgets.base import BaseWidget
from hammett.widgets.exceptions import FailedToGetStateKey, MissingPersistence

if TYPE_CHECKING:
    from typing import Any

    from telegram import Message, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.screen import FinalRenderConfig
    from hammett.types import Keyboard, Stage

_END_POSITION, _START_POSITION = -1, 0


class CarouselWidget(BaseWidget, NotificationScreen, StartScreen):
    """Implements the display of a carousel widget with control buttons
    for a list of images.
    """

    images: list[list[str]] = []
    infinity: bool = False
    back_caption: str = '⏮'
    next_caption: str = '⏭'
    disable_caption: str = '🔚'

    def __init__(self: 'Self') -> None:
        super().__init__()

        if not isinstance(self.images, list):
            msg = f'The images attribute of {self.__class__.__name__} must be a list of lists'
            raise ImproperlyConfigured(msg)

        if not (self.back_caption and self.next_caption and self.disable_caption):
            msg = (
                f'{self.__class__.__name__} must specify both back_caption, next_caption '
                f'and disable_caption'
            )
            raise ImproperlyConfigured(msg)

        self._back_button = Button(
            self.back_caption,
            self._back,
            source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
        )
        self._next_button = Button(
            self.next_caption,
            self._next,
            source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
        )
        self._disabled_button = Button(
            self.disable_caption,
            self._do_nothing,
            source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
        )
        self._infinity_keyboard = [
            [self._back_button, self._next_button],
            *self.add_extra_keyboard(),
        ]

    async def _init(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None' = None,
        images: list[list[str]] | None = None,
    ) -> 'Stage':
        """Initializes the widget."""

        config = config or RenderConfig()
        current_images = images or await self.get_images(update, context)

        cover, description = current_images[_START_POSITION]
        config.cover = cover
        if not config.description:
            config.description = description or self.description

        if self.infinity:
            config.keyboard = self._infinity_keyboard
        else:
            config.keyboard = await self._build_keyboard(current_images, _START_POSITION)

        await self.render(update, context, config=config, extra_data={'images': current_images})
        return DEFAULT_STAGE

    async def _post_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        message: 'Message',
        _config: 'FinalRenderConfig',
        extra_data: 'Any | None',
    ) -> None:
        """Saves to user_data images after screen rendering if it new message."""

        if (not update or not update.callback_query) and extra_data:
            state_key = await self._get_state_key(
                chat_id=message.chat_id,
                message_id=message.message_id,
            )
            try:
                context.user_data[state_key] = {  # type: ignore[index]
                    'images': extra_data.get('images', []),
                }
            except TypeError as exc:  # raised when messages are sent from jobs
                if not context._application.persistence:  # noqa: SLF001
                    msg = (
                        f"It's not possible to pass data to user_data. "
                        f"To solve the issue either don't use {self.__class__.__name__} in jobs "
                        f"or configure persistence."
                    )
                    raise MissingPersistence(msg) from exc
                user_data = cast('UD', {**context._application.user_data})  # noqa: SLF001
                user_data[message.chat_id].update({  # type: ignore[index]
                    state_key: {
                        'images': extra_data.get('images', []),
                        'position': _START_POSITION,
                    },
                })
                await context._application.persistence.update_user_data(  # noqa: SLF001
                    message.chat_id,
                    user_data,
                )

    async def _do_nothing(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Invoked by a disabled control button."""

    async def _build_keyboard(
        self: 'Self',
        images: list[list[str]],
        current_image: int,
    ) -> 'Keyboard':
        """Determines which button to disable and returns the updated keyboard."""

        try:
            images[current_image + 1]
        except IndexError:
            next_button = self._disabled_button
        else:
            next_button = self._next_button

        if current_image - 1 < 0:
            back_button = self._disabled_button
        else:
            try:
                images[current_image - 1]
            except IndexError:
                back_button = self._disabled_button
            else:
                back_button = self._back_button

        return [
            [back_button, next_button],
            *self.add_extra_keyboard(),
        ]

    async def _get_state_value(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        state_key: str,
    ) -> 'Any | None':
        """Safely gets the specified value from the widget state dictionary
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

    async def _set_state_value(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        state_key: str,
        state_value: 'Any',
    ) -> None:
        """Safely sets the specified value to widget state dictionary
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

    async def _switch_handle_method(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        prev_state: int,
        next_state: int,
    ) -> None:
        """Switches handle method."""

        if self.infinity:
            await self._handle_infinity_mode(update, context, next_state)
        else:
            await self._handle_regular_mode(update, context, prev_state, next_state)

    async def _handle_regular_mode(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        prev_state: int,
        next_state: int,
    ) -> None:
        """Handles switching image in a regular mode."""

        images = await self._get_state_value(update, context, 'images') or []

        try:
            cover, description = images[next_state]
        except IndexError:
            state = prev_state
            config = RenderConfig(description=self.description)
        else:
            await self._set_state_value(update, context, 'position', next_state)

            state = next_state
            config = RenderConfig(
                description=description or self.description,
                cover=cover,
            )

        config.keyboard = await self._build_keyboard(images, state)
        return await self.render(update, context, config=config)

    @register_button_handler
    async def _handle_infinity_mode(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        next_state: int,
    ) -> None:
        """Handles switching image in an infinity mode."""

        images = await self._get_state_value(update, context, 'images') or []

        try:
            cover, description = images[next_state]
        except IndexError:
            if next_state == len(images):
                cover, description = images[_START_POSITION]
                await self._set_state_value(update, context, 'position', _START_POSITION)
            else:
                cover, description = images[_END_POSITION]
                await self._set_state_value(update, context, 'position', _END_POSITION)
        else:
            await self._set_state_value(update, context, 'position', next_state)

        config = RenderConfig(
            description=description or self.description,
            cover=cover,
            keyboard=self._infinity_keyboard,
        )
        return await self.render(update, context, config=config)

    @register_button_handler
    async def _next(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switches to the next image."""

        if context.user_data:
            current_image = (await self._get_state_value(update, context, 'position') or
                             _START_POSITION)
        else:
            current_image = _START_POSITION

        return await self._switch_handle_method(
            update,
            context,
            current_image,
            current_image + 1,
        )

    @register_button_handler
    async def _back(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switches to the previous image."""

        current_image = await self._get_state_value(update, context, 'position') or _START_POSITION
        return await self._switch_handle_method(
            update,
            context,
            current_image,
            current_image - 1,
        )

    #
    # Public methods
    #

    async def get_images(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> list[list[str]]:
        """Returns the `images` attribute of the widget."""

        return self.images

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Handles the case when the widget is passed to Button as `GOTO_SOURCE_TYPE`."""

        return await self._init(update, context)

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Handles the case when the widget is used as StartScreen."""

        config = RenderConfig(as_new_message=True)
        return await self._init(update, context, config=config)

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> 'Stage':
        """Handles the case when the widget is used as a notification."""

        config = config or RenderConfig()
        config.as_new_message = True

        images = None
        if extra_data:
            images = extra_data.get('images', None)

        return await self._init(None, context, config=config, images=images)

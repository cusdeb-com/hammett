"""The module contains the implementation of the carousel widget."""

import contextlib
from typing import TYPE_CHECKING

from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.handlers import register_handler
from hammett.core.screen import Button, RenderConfig, StartScreen
from hammett.widgets.base import BaseWidget
from hammett.widgets.exceptions import FailedToGetStateKey

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Keyboard, Stage

_CAROUSEL_START_POSITION = 0


class CarouselWidget(BaseWidget, StartScreen):
    """Implements the display of a carousel with control buttons for a list of images."""

    images: list[list[str]] = []
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

        if self.images:
            self.cover, description = self.images[_CAROUSEL_START_POSITION]
            self.description = description or self.description

    async def _init(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None' = None,
    ) -> 'Stage':
        """Initializes the widget."""

        with contextlib.suppress(FailedToGetStateKey):  # raised when invoked using /start
            current_image_key = await self._get_state_key(update)
            context.user_data[current_image_key] = _CAROUSEL_START_POSITION  # type: ignore[index]

        config = config or RenderConfig()
        config.keyboard = await self._build_keyboard(_CAROUSEL_START_POSITION)

        await self.render(update, context, config=config)
        return DEFAULT_STAGE

    async def _do_nothing(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Invoked by a disabled control button."""

    async def _build_keyboard(self: 'Self', current_image: int) -> 'Keyboard':
        """Determines which button to disable and returns the updated keyboard."""

        try:
            self.images[current_image + 1]
        except IndexError:
            next_button = self._disabled_button
        else:
            next_button = self._next_button

        if current_image - 1 < 0:
            back_button = self._disabled_button
        else:
            try:
                self.images[current_image - 1]
            except IndexError:
                back_button = self._disabled_button
            else:
                back_button = self._back_button

        return [
            [back_button, next_button],
            *self.add_extra_keyboard(),
        ]

    async def _switch(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        prev_state: int,
        next_state: int,
    ) -> None:
        """Handles switching image."""

        try:
            cover, description = self.images[next_state]
        except IndexError:
            state = prev_state
            config = RenderConfig(description=self.description)
        else:
            current_image_key = await self._get_state_key(update)
            context.user_data[current_image_key] = next_state  # type: ignore[index]

            state = next_state
            config = RenderConfig(
                description=description or self.description,
                cover=cover,
            )

        config.keyboard = await self._build_keyboard(state)
        return await self.render(update, context, config=config)

    @register_handler
    async def _next(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switches to the next image."""

        current_image_key = await self._get_state_key(update)

        if context.user_data:
            current_image = context.user_data.get(  # type: ignore[attr-defined]
                current_image_key, _CAROUSEL_START_POSITION,
            )
        else:
            current_image = _CAROUSEL_START_POSITION

        return await self._switch(
            update,
            context,
            current_image,
            current_image + 1,
        )

    @register_handler
    async def _back(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switches to the previous image."""

        current_image_key = await self._get_state_key(update)
        current_image = context.user_data.get(  # type: ignore[union-attr]
            current_image_key, _CAROUSEL_START_POSITION,
        )
        return await self._switch(
            update,
            context,
            current_image,
            current_image - 1,
        )

    #
    # Public methods
    #

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

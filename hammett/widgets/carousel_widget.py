"""The module contains the implementation of the carousel widget."""

from typing import TYPE_CHECKING

from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourcesTypes
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.handlers import register_button_handler
from hammett.widgets.base import BaseWidget

if TYPE_CHECKING:
    from typing import Any

    from telegram import Message, Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.constants import FinalRenderConfig
    from hammett.types import Keyboard, State

_END_POSITION, _START_POSITION = -1, 0


class CarouselWidget(BaseWidget):
    """Implements the display of a carousel widget with control buttons
    for a list of images.
    """

    images: list[list[str]] = []
    infinity: bool = False
    back_caption: str = '⏮'
    next_caption: str = '⏭'
    disable_caption: str = '🔚'

    def __init__(self: 'Self') -> None:
        """Initialize a carousel widget object."""
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
        self._infinity_keyboard = [[self._back_button, self._next_button]]

    async def _init(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None' = None,
        images: list[list[str]] | None = None,
    ) -> 'State':
        """Initialize the widget."""
        config = config or RenderConfig()
        current_images = images or await self.get_images(update, context)

        cover, description = current_images[_START_POSITION]
        config.cover = cover
        if not config.description:
            config.description = description or self.description

        if self.infinity:
            config.keyboard = (self._infinity_keyboard +
                               await self.add_extra_keyboard(update, context))
        else:
            config.keyboard = await self._build_keyboard(
                update,
                context,
                current_images,
                _START_POSITION,
            )

        await self.render(update, context, config=config, extra_data={'images': current_images})
        return DEFAULT_STATE

    async def _initialized_state(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _message: 'Message | tuple[Message]',
        _config: 'FinalRenderConfig',
        extra_data: 'Any',
    ) -> 'dict[Any, Any]':
        """Return the post-initialization widget state to be saved in context."""
        return {
            'images': extra_data.get('images', []),
        }

    async def _do_nothing(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Invoke by a disabled control button."""

    async def _build_keyboard(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        images: list[list[str]],
        current_image: int,
    ) -> 'Keyboard':
        """Determine which button to disable and return the updated keyboard."""
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
            *await self.add_extra_keyboard(update, context),
        ]

    async def _switch_handle_method(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        prev_state: int,
        next_state: int,
    ) -> None:
        """Switch handle method."""
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
        """Handle switching image in a regular mode."""
        images = await self.get_state_value(update, context, 'images') or []

        try:
            cover, description = images[next_state]
        except IndexError:
            state = prev_state
            config = RenderConfig(description=self.description)
        else:
            await self.set_state_value(update, context, 'position', next_state)

            state = next_state
            config = RenderConfig(
                description=description or self.description,
                cover=cover,
            )

        config.keyboard = await self._build_keyboard(update, context, images, state)
        return await self.render(update, context, config=config)

    async def _handle_infinity_mode(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        next_state: int,
    ) -> None:
        """Handle switching image in an infinity mode."""
        images = await self.get_state_value(update, context, 'images') or []

        try:
            cover, description = images[next_state]
        except IndexError:
            if next_state == len(images):
                cover, description = images[_START_POSITION]
                await self.set_state_value(update, context, 'position', _START_POSITION)
            else:
                cover, description = images[_END_POSITION]
                await self.set_state_value(update, context, 'position', _END_POSITION)
        else:
            await self.set_state_value(update, context, 'position', next_state)

        config = RenderConfig(
            description=description or self.description,
            cover=cover,
            keyboard=self._infinity_keyboard + await self.add_extra_keyboard(update, context),
        )
        return await self.render(update, context, config=config)

    @register_button_handler('')
    async def _next(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switch to the next image."""
        if context.user_data:
            current_image = (
                await self.get_state_value(update, context, 'position') or _START_POSITION
            )
        else:
            current_image = _START_POSITION

        return await self._switch_handle_method(
            update,
            context,
            current_image,
            current_image + 1,
        )

    @register_button_handler('')
    async def _back(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> None:
        """Switch to the previous image."""
        current_image = await self.get_state_value(update, context, 'position') or _START_POSITION
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
        """Return the `images` attribute of the widget."""
        return self.images

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is passed to Button as `GOTO_SOURCE_TYPE`."""
        return await self._init(update, context)

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is used as StartScreen."""
        config = RenderConfig(as_new_message=True)
        return await self._init(update, context, config=config)

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> 'State':
        """Handle the case when the widget is used as a notification."""
        config = config or RenderConfig()
        config.as_new_message = True

        images = None
        if extra_data:
            images = extra_data.get('images', None)

        return await self._init(None, context, config=config, images=images)

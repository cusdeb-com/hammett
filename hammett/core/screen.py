"""The module contains the implementation of the screen components
(i.e., cover, description and keyboard).
"""

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, cast

from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue

from hammett.core import handlers
from hammett.core.constants import DEFAULT_STATE, EMPTY_KEYBOARD, FinalRenderConfig, RenderConfig
from hammett.core.exceptions import (
    FailedToGetDataAttributeOfQuery,
    PayloadIsEmpty,
    ScreenDescriptionIsEmpty,
    ScreenRouteIsEmpty,
)
from hammett.core.renderer import Renderer
from hammett.utils.misc import get_callback_query

if TYPE_CHECKING:
    from os import PathLike
    from typing import Any

    from telegram import Message, Update
    from telegram.constants import ParseMode
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Document, Keyboard, Routes, State

LOGGER = logging.getLogger(__name__)


class Screen:
    """The class implements the interface of a screen."""

    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    document: 'Document | None' = None
    html_parse_mode: 'ParseMode | DefaultValue[None]' = DEFAULT_NONE
    routes: 'Routes | None' = None
    renderer_class = Renderer

    _initialized: bool = False
    _instance: 'Screen | None' = None

    def __init__(self: 'Self') -> None:
        if not self._initialized:
            if self.html_parse_mode is DEFAULT_NONE:
                from hammett.conf import settings
                self.html_parse_mode = settings.HTML_PARSE_MODE

                self.renderer = Renderer(self.html_parse_mode)  # type: ignore[arg-type]

            self._initialized = True

    def __new__(cls: type['Screen'], *args: 'Any', **kwargs: 'Any') -> 'Screen':
        """Implements the singleton pattern."""

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    async def _finalize_config(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None',
    ) -> 'FinalRenderConfig':
        """Finalizes an object of RenderConfig returning an object of FinalRenderConfig."""

        final_config = FinalRenderConfig(**asdict(config)) if config else FinalRenderConfig()
        final_config.cache_covers = (
            final_config.cache_covers or await self.get_cache_covers(update, context)
        )
        final_config.cover = final_config.cover or await self.get_cover(update, context)

        final_config.description = (
            final_config.description or await self.get_description(update, context)
        )
        final_config.document = final_config.document or await self.get_document(update, context)
        if (
            not final_config.description and not final_config.document and
            not final_config.attachments
        ):
            msg = f'The description of {self.__class__.__name__} is empty'
            raise ScreenDescriptionIsEmpty(msg)

        if not config or config.keyboard is None:
            final_config.keyboard = final_config.keyboard or self.setup_keyboard()

        return final_config

    async def _pre_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
        extra_data: 'Any | None',
    ) -> 'Message | None':
        """Runs before screen rendering."""

    async def _post_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        message: 'Message',
        config: 'FinalRenderConfig',
        extra_data: 'Any | None',
    ) -> None:
        """Runs after screen rendering."""

    #
    # Public methods
    #

    async def get_cache_covers(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Returns the `cache_covers` attribute of the screen."""

        return self.cache_covers

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'RenderConfig':
        """Returns the Screen's config."""

        return RenderConfig()

    async def get_cover(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'str | PathLike[str]':
        """Returns the `cover` attribute of the screen."""

        return self.cover

    async def get_current_state(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Returns the current state."""

        return cast('State', context.user_data.get('current_state'))  # type: ignore[union-attr]

    async def get_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Returns the `description` attribute of the screen."""

        return self.description

    async def get_document(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Document | None':
        """Returns the `document` attribute of the screen."""

        return self.document

    async def get_payload(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Returns the payload passed through the pressed button."""

        query = await get_callback_query(update)
        data = getattr(query, 'data', None)
        if data is None:
            raise FailedToGetDataAttributeOfQuery

        try:
            payload_storage = handlers.get_payload_storage(context)
            return payload_storage.pop(data)
        except KeyError as exc:
            raise PayloadIsEmpty from exc

    async def render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> None:
        """Renders the screen components (i.e., cover, description and keyboard)."""

        final_config = await self._finalize_config(update, context, config)
        await self._pre_render(update, context, final_config, extra_data)

        message = await self.renderer.render(update, context, final_config, extra_data)
        if message:
            await self._post_render(update, context, message, final_config, extra_data)

    def setup_keyboard(self: 'Self') -> 'Keyboard':
        """Sets up the keyboard for the screen."""

        return EMPTY_KEYBOARD

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switches to the screen re-rendering the previous message."""

        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switches to the screen sending it as a new message."""

        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        extra_data: 'Any | None' = None,
    ) -> 'State':
        """Sends the screen to the specified chat."""

        config = config or RenderConfig()
        config.as_new_message = True

        await self.render(None, context, config=config, extra_data=extra_data)
        return DEFAULT_STATE


class RouteMixin(Screen):
    """Mixin to switch between screens which are registered
    in different states.
    """

    def __init__(self: 'Self') -> None:
        super().__init__()

        if self.routes is None:
            msg = f'The route of {self.__class__.__name__} is empty'
            raise ScreenRouteIsEmpty(msg)

    async def _get_return_state_from_routes(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        routes: 'Routes',
    ) -> 'State':
        """Returns the first found state in the routes."""

        current_state = await self.get_current_state(update, context)

        for route in routes:
            route_states, return_state = route
            if current_state in route_states:
                return return_state

        return current_state

    async def sgoto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Changes the state and switches to the screen re-rendering
        the previous message.
        """

        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return await self._get_return_state_from_routes(
            update, context, self.routes,  # type: ignore[arg-type]
        )

    async def sjump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Changes the state and switches to the screen sending
        it as a new message.
        """

        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return await self._get_return_state_from_routes(
            update, context, self.routes,  # type: ignore[arg-type]
        )


class StartScreen(Screen):
    """The base class for start screens (i.e, the screens
    that show up on the /start command).
    """

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoked on the /start command."""

        return await self.jump(update, context)

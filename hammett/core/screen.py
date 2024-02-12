"""The module contains the implementation of the screen components
(i.e., cover, description and keyboard).
"""

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, cast

from telegram._utils.defaultvalue import DEFAULT_NONE

from hammett.core import handlers
from hammett.core.constants import DEFAULT_STATE, EMPTY_KEYBOARD, FinalRenderConfig, RenderConfig
from hammett.core.exceptions import (
    FailedToGetDataAttributeOfQuery,
    PayloadIsEmpty,
    ScreenDescriptionIsEmpty,
)
from hammett.core.renderer import Renderer
from hammett.utils.misc import get_callback_query
from hammett.utils.render_config import get_latest_msg_config, save_latest_msg_config

if TYPE_CHECKING:
    from os import PathLike
    from typing import Any

    from telegram import Message, Update
    from telegram._utils.defaultvalue import DefaultValue
    from telegram.constants import ParseMode
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Document, Keyboard, State

LOGGER = logging.getLogger(__name__)


class Screen:
    """The class implements the interface of a screen."""

    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    document: 'Document | None' = None
    html_parse_mode: 'ParseMode | DefaultValue[None]' = DEFAULT_NONE
    hide_keyboard: bool = False
    renderer_class = Renderer

    _initialized: bool = False
    _instance: 'Screen | None' = None

    def __init__(self: 'Self') -> None:
        """Initialize a screen object."""
        if not self._initialized:
            if self.html_parse_mode is DEFAULT_NONE:
                from hammett.conf import settings
                self.html_parse_mode = settings.HTML_PARSE_MODE

            self.renderer = Renderer(self.html_parse_mode)  # type: ignore[arg-type]

            self._initialized = True

    def __new__(cls: type['Screen'], *args: 'Any', **kwargs: 'Any') -> 'Screen':
        """Implement the singleton pattern."""
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    #
    # Private methods
    #

    async def _finalize_config(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None',
    ) -> 'FinalRenderConfig':
        """Finalize an object of RenderConfig returning an object of FinalRenderConfig."""
        final_config = FinalRenderConfig(**asdict(config)) if config else FinalRenderConfig()
        final_config.cache_covers = (
            final_config.cache_covers or await self.get_cache_covers(update, context)
        )
        final_config.cover = final_config.cover or await self.get_cover(update, context)
        final_config.chat_id = final_config.chat_id or context._chat_id  # noqa: SLF001
        final_config.hide_keyboard = (
            final_config.hide_keyboard or await self.get_hide_keyboard(update, context)
        )

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
            final_config.keyboard = (
                final_config.keyboard or await self.add_default_keyboard(update, context)
            )

        if not final_config.message_id and update:
            query = await get_callback_query(update)
            if query and query.message:
                final_config.message_id = query.message.message_id

        return final_config

    async def _pre_render(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'FinalRenderConfig',
        **kwargs: 'Any',
    ) -> 'Message | None':
        """Run before screen rendering."""

    async def _post_render(
        self: 'Self',
        update: 'Update | None',  # noqa: ARG002
        context: 'CallbackContext[BT, UD, CD, BD]',
        message: 'Message | tuple[Message]',
        config: 'FinalRenderConfig',
        **kwargs: 'Any',  # noqa: ARG002
    ) -> None:
        """Run after screen rendering."""
        from hammett.conf import settings

        if isinstance(message, tuple):
            message = message[-1]

        if config.as_new_message:
            prev_msg_config = get_latest_msg_config(context, message)
            if prev_msg_config and prev_msg_config['hide_keyboard']:
                await self.renderer.hide_keyboard(context, prev_msg_config)

        if settings.SAVE_LATEST_MESSAGE:
            config.keyboard = None  # type: ignore[assignment]
            await save_latest_msg_config(context, config, message)
        elif config.hide_keyboard:
            LOGGER.warning(
                'The keyboard hiding feature does not work without '
                'the SAVE_LATEST_MESSAGE setting set to True, so either '
                'set the hide_keyboard attribute of your screen to False or '
                'set the SAVE_LATEST_MESSAGE setting to True.',
            )

    #
    # Public methods
    #

    async def add_default_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Keyboard':
        """Set up the default keyboard for the screen."""
        return EMPTY_KEYBOARD

    async def get_cache_covers(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Return the `cache_covers` attribute of the screen."""
        return self.cache_covers

    async def get_config(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> 'RenderConfig':
        """Return the Screen's config."""
        return RenderConfig()

    async def get_cover(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'str | PathLike[str]':
        """Return the `cover` attribute of the screen."""
        return self.cover

    async def get_current_state(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Return the current state."""
        return cast('State', context.user_data.get('current_state'))  # type: ignore[union-attr]

    async def get_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Return the `description` attribute of the screen."""
        return self.description

    async def get_document(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Document | None':
        """Return the `document` attribute of the screen."""
        return self.document

    async def get_hide_keyboard(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Return the `hide_keyboard` attribute of the screen."""
        return self.hide_keyboard

    @staticmethod
    async def get_payload(
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Return the payload passed through the pressed button."""
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
        **kwargs: 'Any',
    ) -> None:
        """Render the screen components (i.e., cover, description and keyboard)."""
        final_config = await self._finalize_config(update, context, config)
        await self._pre_render(update, context, final_config, **kwargs)

        message = await self.renderer.render(update, context, final_config, **kwargs)
        if message:
            await self._post_render(update, context, message, final_config, **kwargs)

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switch to the screen sending it as a new message."""
        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def move(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Switch to the screen re-rendering the previous message."""
        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return DEFAULT_STATE

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        **kwargs: 'Any',
    ) -> 'State':
        """Send the screen to the specified chat."""
        config = config or RenderConfig()
        config.as_new_message = True

        await self.render(None, context, config=config, **kwargs)
        return DEFAULT_STATE

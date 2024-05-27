"""The module contains mixins."""

from typing import TYPE_CHECKING

from hammett.core import Screen
from hammett.core.exceptions import ScreenRouteIsEmpty

if TYPE_CHECKING:
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.types import Routes, State


class RouteMixin(Screen):
    """Mixin to switch between screens which are registered
    in different states.
    """

    routes: 'Routes | None' = None

    def __init__(self: 'Self') -> None:
        super().__init__()

        if self.routes is None:
            msg = f'The route of {self.__class__.__name__} is empty'
            raise ScreenRouteIsEmpty(msg)

    async def _get_return_state_from_routes(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Returns the first found state in the routes."""

        current_state = await self.get_current_state(update, context)

        for route in self.routes:  # type: ignore[union-attr]
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
        return await self._get_return_state_from_routes(update, context)

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
        return await self._get_return_state_from_routes(update, context)


class StartMixin(Screen):
    """Mixin for start screens (i.e, the screens that show up on the /start command)."""

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoked on the /start command."""

        return await self.jump(update, context)

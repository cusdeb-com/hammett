"""The module contains mixins."""

from typing import TYPE_CHECKING, cast

from hammett.conf import settings
from hammett.core import Screen
from hammett.core.exceptions import ImproperlyConfiguredError, ScreenRouteIsEmptyError

if TYPE_CHECKING:
    from typing import Any, Self

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.types.core import Routes, State


class I18NMixin(Screen):
    """The mixin used for screens that support translation into multiple languages."""

    async def get_language_code(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **_kwargs: 'Any',
    ) -> str:
        """Return the language code.

        Returns:
            Current language code.

        """
        if context.user_data is None:
            language_code = settings.LANGUAGE_CODE
        else:
            user_data = cast('dict[str, Any]', context.user_data)
            language_code = user_data.get('language_code', settings.LANGUAGE_CODE)

        return cast('str', language_code)

    async def set_language_code(
        self: 'Self',
        _update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        language_code: str,
        **_kwargs: 'Any',
    ) -> None:
        """Set the language code."""
        if context.user_data is not None:
            user_data = cast('dict[str, Any]', context.user_data)
            user_data['language_code'] = language_code


class RouteMixin(Screen):
    """Mixin to switch between screens which are registered
    in different states.
    """

    routes: 'Routes | None' = None

    def __init__(self: 'Self') -> None:
        """Initialize a route mixin object.

        Raises:
            ScreenRouteIsEmptyError: If the `routes` attribute of the mixin is empty.
            ImproperlyConfiguredError: If the `routes` attribute of the mixin is not
            a tuple with tuples.

        """
        super().__init__()

        if self.routes is None:
            msg = f'The `routes` attribute of {self.__class__.__name__} is empty'
            raise ScreenRouteIsEmptyError(msg)

        if not all(isinstance(item, tuple) for item in self.routes):
            msg = f'The `routes` attribute of {self.__class__.__name__} must be a tuple of tuples.'
            raise ImproperlyConfiguredError(msg)

    def get_return_state_from_routes(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Return the first found state in the routes.

        Returns:
            First found state in the states declared in a `routes`
            attribute of the mixin.

        """
        current_state = self.get_current_state(context)

        if self.routes:
            for route in self.routes:
                route_states, return_state = route
                if current_state in route_states:
                    return return_state

        return current_state

    async def jump_along_route(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Change the state and switch to the screen sending
        it as a new message.

        Returns:
            State after jumping to the screen.

        """
        config = await self.get_config(update, context, **kwargs)
        config.as_new_message = True

        await self.render(update, context, config=config)
        return self.get_return_state_from_routes(context)

    async def move_along_route(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Change the state and switch to the screen re-rendering
        the previous message.

        Returns:
            State after moving to the screen.

        """
        config = await self.get_config(update, context, **kwargs)

        await self.render(update, context, config=config)
        return self.get_return_state_from_routes(context)


class StartMixin(Screen):
    """Mixin for start screens (i.e, the screens that show up on the /start command)."""

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoke on the /start command.

        Returns:
            State after invoking /start command.

        """
        return await self.jump(update, context)

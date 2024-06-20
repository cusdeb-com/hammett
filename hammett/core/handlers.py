"""The module contains the routines to ensure the functioning of handlers."""

import inspect
import logging
import zlib
from contextlib import suppress
from functools import wraps
from typing import TYPE_CHECKING, Any, cast

from hammett.core.exceptions import CommandNameIsEmpty, StatesAttributeIsNotSupported
from hammett.types import HandlerAlias, HandlerType, State

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from telegram.ext.filters import BaseFilter

    from hammett.types import Handler, PayloadStorage

LOGGER = logging.getLogger(__name__)


def _clear_command_name(command_name: str) -> str:
    """Clear the specified command name.

    Raise `CommandNameIsEmpty` if the name either is empty or consists only of '/'.
    """
    if command_name and command_name[0] == '/':
        command_name = command_name[1:]

    if not command_name.strip():
        raise CommandNameIsEmpty

    return command_name


def _get_handler_name(handler: 'Handler') -> str:
    """Return the full name of the specified handler."""
    try:
        return f'{type(handler.__self__).__name__}.{handler.__name__}'
    except AttributeError:  # when a handler is static
        return f'{handler.__qualname__}'


def _register_handler(
    name: str,
    value: HandlerType,
) -> 'Callable[[str], Callable[[HandlerAlias], Handler]]':
    """Set the specified attribute of the decorated handler."""

    def create_decorator(
        command_name: str = '',
        filters: 'BaseFilter | None' = None,
        states: 'Iterable[State] | None' = None,
    ) -> 'Callable[[HandlerAlias], Handler]':
        def decorator(func: 'HandlerAlias') -> 'Handler':
            handler = cast('Handler', func)
            setattr(handler, name, value)
            handler.permissions_ignored = []
            handler.filters = filters

            if states:
                if value != HandlerType.BUTTON_HANDLER:
                    msg = f"{value} is not support 'states' attribute."
                    raise StatesAttributeIsNotSupported(msg)

                handler.states = states

            if value == HandlerType.COMMAND_HANDLER:
                try:
                    handler.command_name = _clear_command_name(command_name)
                except CommandNameIsEmpty as exc:
                    msg = (
                        f"Unable to register the '{handler.__name__}' handler for "
                        f"a command with an empty name."
                    )
                    raise CommandNameIsEmpty(msg) from exc

            @wraps(handler)
            async def wrapper(
                *args: 'Any',
                **kwargs: 'Any',
            ) -> 'Any':
                return await handler(*args, **kwargs)
            return cast('Handler', wrapper)
        return decorator
    return create_decorator


def calc_checksum(obj: 'Any') -> str:
    """Calculate a checksum of the specified object."""
    if callable(obj):  # in a case of a handler
        handler_name = _get_handler_name(obj)
        return str(zlib.adler32(handler_name.encode('utf8')))

    if isinstance(obj, str):  # in a case of a button caption
        return str(zlib.adler32(obj.encode('utf8')))

    raise TypeError


def get_payload_storage(context: 'CallbackContext[BT, UD, CD, BD]') -> 'PayloadStorage':
    """Return the payload storage."""
    from hammett.conf import settings
    namespace = settings.PAYLOAD_NAMESPACE
    bot_data = cast('dict[str, PayloadStorage]', context.bot_data)
    try:
        return bot_data[namespace]
    except KeyError:
        bot_data[namespace] = {}
        return bot_data[namespace]


def log_unregistered_handler(obj: 'Any') -> None:
    """Check the specified object, and if it resembles an unregistered handler,
    log a WARNING message about it.
    """
    if not callable(obj):
        return

    mandatory_params = {'context', 'update'}
    mandatory_return_annotations = {'State', State, inspect.Signature.empty}

    try:
        signature = inspect.signature(obj)
    except ValueError:
        return

    params = set(signature.parameters.keys())
    with suppress(KeyError):  # remove optional parameters from the list
        params.remove('args')
        params.remove('kwargs')
        params.remove('self')

    if (
        len(params) == len(mandatory_params) and
        params.intersection(mandatory_params) == mandatory_params and
        signature.return_annotation in mandatory_return_annotations
    ):
        LOGGER.warning(
            '%s resembles a handler. Perhaps you forgot to register it.',
            _get_handler_name(obj),
        )


register_button_handler = _register_handler('handler_type', HandlerType.BUTTON_HANDLER)
register_button_handler.__doc__ = 'Registers the specified screen method as a button click handler.'

register_command_handler = _register_handler('handler_type', HandlerType.COMMAND_HANDLER)
register_command_handler.__doc__ = 'Registers the specified screen method as a command handler.'

register_input_handler = _register_handler('handler_type', HandlerType.INPUT_HANDLER)
register_input_handler.__doc__ = 'Registers the specified screen method as an input handler.'

_register_typing_handler = _register_handler('handler_type', HandlerType.TYPING_HANDLER)
register_typing_handler = _register_typing_handler('')
register_typing_handler.__doc__ = 'Registers the specified screen method as a typing handler.'

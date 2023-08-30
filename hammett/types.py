"""The module contains the types used throughout the framework."""

from collections.abc import Callable, Coroutine, Iterable
from enum import Enum
from typing import TYPE_CHECKING, Any, NewType, ParamSpec, Protocol, TypeVar
from uuid import UUID

from telegram import Update
from telegram.ext import BaseHandler, CallbackContext
from telegram.ext._utils.types import BD, BT, CCT, CD, UD, ConversationKey

from hammett.core.screen import Button, Screen

if TYPE_CHECKING:
    from typing_extensions import Self

CheckUpdateType = tuple[object, ConversationKey, BaseHandler[Update, CCT], object]

Keyboard = list[list[Button]]

NativeStates = dict[object, list[BaseHandler]]  # type: ignore[type-arg]

PayloadStorage = dict[str, str]

States = dict[int, Iterable[type[Screen]]]

Func = TypeVar('Func', bound=Callable[..., Any])

Stage = NewType('Stage', int)

HandlerR = Coroutine[Any, Any, Stage]

P = ParamSpec('P')

R_co = TypeVar('R_co', covariant=True)


class HandlerType(Enum):
    """The class enumerates all types of handlers."""

    button_handler = 'button_handler'


class Handler(Protocol[P, R_co]):
    """The class implements the Handler type."""

    __name__: str  # noqa: A003
    __self__: Screen
    __qualname__: str
    handler_type: HandlerType
    permissions_ignored: list[UUID]

    def __call__(
        self: 'Self',
        screen: 'Screen',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *args: 'Any',
        **kwargs: 'Any',
    ) -> HandlerR:
        """The signature is required for every handler of the Handler type."""
        ...


Source = str | type[Screen] | Handler

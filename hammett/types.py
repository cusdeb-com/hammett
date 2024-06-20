"""The module contains the types used throughout the framework."""

from collections.abc import Awaitable, Callable, Coroutine, Iterable, Sequence
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType, Protocol, TypedDict, TypeVar
from uuid import UUID

import telegram
from telegram import Update
from telegram._utils.types import FileInput
from telegram.ext import BaseHandler, CallbackContext
from telegram.ext._utils.types import BD, BT, CCT, CD, UD, ConversationKey
from telegram.ext.filters import BaseFilter

from hammett.core.button import Button
from hammett.core.screen import Screen

if TYPE_CHECKING:
    from typing_extensions import Self

CheckUpdateType = tuple[object, ConversationKey, BaseHandler[Update, CCT], object]


class Document(TypedDict):
    """The class implements the Document type."""

    data: FileInput
    name: str


Keyboard = list[list[Button]]

NativeStates = dict[object, list[BaseHandler]]  # type: ignore[type-arg]

PayloadStorage = dict[str, str]

State = NewType('State', str)

States = dict[State, Iterable[type[Screen]]]

Func = TypeVar('Func', bound=Callable[..., Any])

Attachments = (
    Sequence[telegram.InputMediaAudio] | Sequence[telegram.InputMediaDocument] |
    Sequence[telegram.InputMediaPhoto] | Sequence[telegram.InputMediaVideo]
)


class HandlerType(Enum):
    """The class enumerates all types of handlers."""

    BUTTON_HANDLER = auto()
    COMMAND_HANDLER = auto()
    INPUT_HANDLER = auto()
    TYPING_HANDLER = auto()


class Handler(Protocol):
    """The class implements the Handler type."""

    __name__: str
    __self__: Screen
    __qualname__: str
    command_name: str
    filters: BaseFilter | None
    handler_type: HandlerType
    permissions_ignored: list[UUID]
    states: Iterable[State]

    # Callback protocols and Callable types can be used mostly interchangeably.
    # Argument names in __call__ methods must be identical, unless a double
    # underscore prefix is used.
    # See: https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
    def __call__(
        self: 'Self',
        __update: 'Update',
        __context: 'CallbackContext[BT, UD, CD, BD]',
        *args: 'Any',
        **kwargs: 'Any',
    ) -> Awaitable[Any]:
        """Represent the signature which is required for every handler
        of the Handler type.
        """
        ...


HandlerAlias = Callable[..., Coroutine[Any, Any, Any]]

Routes = tuple[tuple[set[State], State]]

Source = str | type[Screen] | Handler | HandlerAlias

"""The module contains the constants used in the core."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from os import PathLike

    from hammett.types import Attachments, Document, Keyboard, State

# Use 'cast' instead of 'State(0)' to avoid a circular import
DEFAULT_STATE = cast('State', '0')

EMPTY_KEYBOARD: 'Keyboard' = []


class SourcesTypes(Enum):
    """The class contains the available types of sources."""

    GOTO_SOURCE_TYPE = auto()
    HANDLER_SOURCE_TYPE = auto()
    JUMP_SOURCE_TYPE = auto()
    URL_SOURCE_TYPE = auto()


@dataclass
class RenderConfig:
    """The class that represents a config for the Screen render method."""

    chat_id: int = 0
    as_new_message: bool = False
    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    attachments: 'Attachments | None' = None
    document: 'Document | None' = None
    keyboard: 'Keyboard | None' = None


@dataclass
class FinalRenderConfig(RenderConfig):
    """The class represents a final config intended for
    the Screen render method.
    """

    keyboard: 'Keyboard' = field(default_factory=list)

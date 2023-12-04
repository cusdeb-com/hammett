"""The module contains the constants used in the core."""

from enum import Enum, auto
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from hammett.types import State

# Use 'cast' instead of 'State(0)' to avoid a circular import
DEFAULT_STATE = cast('State', 0)


class SourcesTypes(Enum):
    """The class contains the available types of sources."""

    GOTO_SOURCE_TYPE = auto()
    HANDLER_SOURCE_TYPE = auto()
    URL_SOURCE_TYPE = auto()

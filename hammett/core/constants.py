"""The module contains the constants used in the core."""

from enum import Enum, auto
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from hammett.types import Stage

# Use 'cast' instead of 'Stage(0)' to avoid a circular import
DEFAULT_STAGE = cast('Stage', 0)

PAYLOAD_DELIMITER = ','


class SourcesTypes(Enum):
    """The class contains the available types of sources."""

    GOTO_SOURCE_TYPE = auto()
    HANDLER_SOURCE_TYPE = auto()
    URL_SOURCE_TYPE = auto()

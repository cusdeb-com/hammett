"""The module contains the constants used in the core."""

from enum import Enum, auto
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from hammett.types import Stage

# Use 'cast' instead of 'Stage(0)' to avoid a circular import
DEFAULT_STAGE = cast('Stage', 0)

MAX_DATA_SIZE = 64

PAYLOAD_DELIMITER = ','

STR_BUFFER_SIZE_FOR_HANDLER = 10  # a string buffer size for an unsigned 32bit integer

STR_BUFFER_SIZE_FOR_PAYLOAD = MAX_DATA_SIZE - (STR_BUFFER_SIZE_FOR_HANDLER + len(PAYLOAD_DELIMITER))


class SourcesTypes(Enum):
    """The class contains the available types of sources."""

    GOTO_SOURCE_TYPE = auto()
    HANDLER_SOURCE_TYPE = auto()
    URL_SOURCE_TYPE = auto()

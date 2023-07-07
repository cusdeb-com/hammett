"""The module contains the constants used in the core. """

from enum import Enum, auto

DEFAULT_STAGE = 0


class SourcesTypes(Enum):
    """The class contains the available types of sources. """

    GOTO_SOURCE_TYPE = auto()
    HANDLER_SOURCE_TYPE = auto()
    URL_SOURCE_TYPE = auto()

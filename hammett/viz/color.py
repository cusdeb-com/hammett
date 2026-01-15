"""The method contains functions for working with the std output style."""

from enum import Enum


class Style(Enum):
    """Contains output styles."""

    RESET = '\x1b[0m'
    ERROR = '\x1b[31m'
    SUCCESS = '\x1b[32m'
    WARNING = '\x1b[33m'


def colorize(style: 'Style', text: str) -> str:
    """Return string with the selected style and resetting it at the end.

    Returns
    -------
        String with the selected style.

    """
    return f'{style.value}{text}{Style.RESET.value}'

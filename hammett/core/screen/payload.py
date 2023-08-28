"""The module contains the routines to ensure the functioning of payload."""

import zlib
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.types import PayloadStorage


def calc_checksum(obj: 'Any') -> str:
    """Calculates a checksum of the specified object."""

    if callable(obj):  # in a case of a handler
        try:
            func_name = f'{type(obj.__self__).__name__}.{obj.__name__}'
        except AttributeError:  # when a handler is static
            func_name = f'{obj.__qualname__}'

        return str(zlib.adler32(func_name.encode('utf8')))

    if isinstance(obj, str):  # in a case of a button caption
        return str(zlib.adler32(obj.encode('utf8')))

    raise TypeError


def get_payload_storage(context: 'CallbackContext[BT, UD, CD, BD]') -> 'PayloadStorage':
    """Returns the payload storage."""

    from hammett.conf import settings
    namespace = settings.PAYLOAD_NAMESPACE
    bot_data = cast('dict[str, PayloadStorage]', context.bot_data)
    try:
        return bot_data[namespace]
    except KeyError:
        bot_data[namespace] = {}
        return bot_data[namespace]

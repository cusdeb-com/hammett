"""Default Hammett settings. Override these using the module specified via
the HAMMETT_SETTINGS_MODULE environment variable.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# Sets the waiting timeout for the read_timeout parameter of telegram.Bot.request.
# https://docs.python-telegram-bot.org/en/stable/telegram.ext.applicationbuilder.html#telegram.ext.ApplicationBuilder.read_timeout
APPLICATION_BUILDER_READ_TIMEOUT = 5.0

DOMAIN = 'hammett'

ERROR_HANDLER_CONF = {
    'IGNORE_QUERY_IS_TOO_OLD': False,
    'IGNORE_TIMED_OUT': False,
    'IGNORE_UPDATE_MASSAGE_FAIL': False,
}

HIDERS_CHECKER = ''

LANGUAGE_CODE = 'en'

LOCALE_PATHS: list[str] = []

LOGGING: dict[str, 'Any'] = {}

PAYLOAD_NAMESPACE = 'hammett'

PERMISSIONS: list[str] = []

REDIS_CONF = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'PASSWORD': None,
    'UNIX_SOCKET_PATH': None,
}

REDIS_CACHE = {
    **REDIS_CONF,
    'DB': 1,
}

REDIS_PERSISTENCE = {
    **REDIS_CONF,
    'DB': 0,
}

SAVE_LATEST_MESSAGE = False

SEND_METHODS_READ_TIMEOUT = None

TOKEN = ''

USE_WEBHOOK = False

WEBHOOK_LISTEN = '127.0.0.1'

WEBHOOK_PORT = 80

WEBHOOK_URL_PATH = ''

WEBHOOK_URL = ''

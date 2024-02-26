"""
Default Hammett settings. Override these using the module specified via
the HAMMETT_SETTINGS_MODULE environment variable.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

DOMAIN = 'hammett'

HIDERS_CHECKER = ''

HTML_PARSE_MODE = True

LANGUAGE_CODE = 'en'

LOCALE_PATH = ''

LOGGING: dict[str, 'Any'] = {}

PAYLOAD_NAMESPACE = 'hammett'

PERMISSIONS: list[str] = []

REDIS_PERSISTENCE = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}

SAVE_LATEST_MESSAGE = False

TOKEN = ''

USE_WEBHOOK = False

WEBHOOK_LISTEN = '127.0.0.1'

WEBHOOK_PORT = 80

WEBHOOK_URL_PATH = ''

WEBHOOK_URL = ''

"""
Default Hammett settings. Override these using the module specified via
the HAMMETT_SETTINGS_MODULE environment variable.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from hammett.core.permissions import Permission

HIDERS_CHECKER = ''

HTML_PARSE_MODE = True

LOGGING: dict[str, 'Any'] = {}

PERMISSIONS: list[type['Permission']] = []

REDIS_PERSISTENCE = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}

TOKEN = ''

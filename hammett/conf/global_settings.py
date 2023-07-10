"""
Default Hammett settings. Override these using the module specified via
the HAMMETT_SETTINGS_MODULE environment variable.
"""

HIDERS_CHECKER = ''

HTML_PARSE_MODE = True

PERMISSIONS = []

REDIS_PERSISTENCE = {
    'HOST': '127.0.0.1',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
}

TOKEN = ''

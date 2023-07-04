"""
Default Hammett settings. Override these using the module specified via
the HAMMETT_SETTINGS_MODULE environment variable.
"""

import os


HIDERS_CHECKER = ''

HTML_PARSE_MODE = True

PERMISSIONS = []

TOKEN = os.getenv('TOKEN', '')

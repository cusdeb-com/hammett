"""The module contains the settings of the demo."""

import contextlib
import os

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv
    load_dotenv()

ERROR_HANDLER_CONF = {
    'IGNORE_QUERY_IS_TOO_OLD': False,
    'IGNORE_TIMED_OUT': False,
    'IGNORE_UPDATE_MASSAGE_FAIL': True,
}

REDIS_PERSISTENCE = {
    'HOST': os.getenv('REDIS_PERSISTENCE_HOST', 'valkey'),
    'PORT': 6379,
    'DB': os.getenv('REDIS_PERSISTENCE_DB', '1'),
}

TOKEN = os.getenv('TOKEN', '')

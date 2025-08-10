"""The module contains the settings of the demo."""

import contextlib
import os

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv
    load_dotenv()

LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname}: {name}: {asctime}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'formatter': 'standard',
            'level': LOGGING_LEVEL,
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'hammett': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
        },
    },
}

REDIS_PERSISTENCE = {
    'HOST': os.getenv('REDIS_PERSISTENCE_HOST', 'valkey'),
    'PORT': 6379,
    'DB': os.getenv('REDIS_PERSISTENCE_DB', '1'),
}

TOKEN = os.getenv('TOKEN', '')

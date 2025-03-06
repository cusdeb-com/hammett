"""The module contains the settings of the demo."""

import contextlib
import os
from pathlib import Path

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv
    load_dotenv()

MEDIA_ROOT = Path(__file__).resolve().parent / 'media'

REDIS_PERSISTENCE = {
    'HOST': os.getenv('REDIS_PERSISTENCE_HOST', 'valkey'),
    'PORT': 6379,
    'DB': os.getenv('REDIS_PERSISTENCE_DB', '1'),
}

TOKEN = os.getenv('TOKEN', '')

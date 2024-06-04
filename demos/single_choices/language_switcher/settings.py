import os
from pathlib import Path

LOCALE_PATH = Path(__file__).resolve().parent / 'locale'

TOKEN = os.getenv('TOKEN', '')

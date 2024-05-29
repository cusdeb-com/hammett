"""The module contains facilities for configuring logging in Hammett."""

import logging
import logging.config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Final

DEFAULT_LOGGING: 'Final' = {
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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'hammett': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


def configure_logging(logging_settings: dict[str, 'Any']) -> None:
    """Configures logging with either the given settings or default settings."""
    logging.config.dictConfig(DEFAULT_LOGGING)

    if logging_settings:
        logging.config.dictConfig(logging_settings)

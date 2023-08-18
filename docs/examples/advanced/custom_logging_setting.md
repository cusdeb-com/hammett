```python
import os


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
            'level': os.getenv('LOG_LEVEL_CONSOLE', 'INFO'),
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'hammett': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL_HAMMETT', 'INFO'),
        },
    },
}
```

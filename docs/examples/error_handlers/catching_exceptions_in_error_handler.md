```python
import logging

LOGGER = logging.getLogger(__name__)


async def error_handler(update, context):
    if isinstance(context.error, IndexError):
        LOGGER.warning('IndexError')
```

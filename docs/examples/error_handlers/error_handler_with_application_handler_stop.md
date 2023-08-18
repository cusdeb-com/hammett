```python
import logging
from telegram.ext import ApplicationHandlerStop

LOGGER = logging.getLogger(__name__)


async def error_handler(context) :
    # Interrupt the sequence of registered error handlers calls
    if isinstance(context.error, KeyError):
        LOGGER.warning('KeyError was handled')
        raise ApplicationHandlerStop
```

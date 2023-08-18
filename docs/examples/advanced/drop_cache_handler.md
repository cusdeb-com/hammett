```python
from hammett.core.cache import CACHE_REDIS_CLI
from hammett.core.handlers import register_button_handler


@register_button_handler
async def drop_cache(self, update, context):
    await CACHE_REDIS_CLI.flushdb()

    return await CacheDroppingSuccess().move(update, context)
```

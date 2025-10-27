```python
import httpx
from hammett.core.cache import cache


class ApiClient:
    def __init__(self):
        self._session = httpx.AsyncClient()

    @cache(60 * 60)
    async def _get_caption_with_cache(self, *_args, **_kwargs):
        return await self._session.get('https://your/path/to/url/')

    async def get_caption(self, drop_cache=False):
        if drop_cache:
            return await self._get_caption_with_cache('https://your/path/to/url/', drop_cache=drop_cache)

        return await self._get_caption_with_cache('https://your/path/to/url/')
```

```python
import httpx
from hammett.core.cache import cache


class ApiClient:
    def __init__(self):
        self._session = httpx.AsyncClient()

    @cache(60 * 60)
    async def get_caption(self):
        return await self._session.get('https://your/path/to/url/')
```

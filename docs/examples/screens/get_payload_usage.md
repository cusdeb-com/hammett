```python
from hammett.core import Screen


class MyScreen(Screen):
    async def get_description(self, update, context, **kwargs):
        payload = await self.get_payload(update, context)
        return payload
```

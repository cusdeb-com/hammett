```python
from hammett.core.handlers import register_button_handler


@register_button_handler
async def handler(self, update, context):
    payload = await self.get_payload(update, context)  # successfully got payload
    await self.get_payload(update, context)  # PayloadIsEmpty
    ...
```

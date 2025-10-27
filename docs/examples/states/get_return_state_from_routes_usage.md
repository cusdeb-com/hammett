```python
from hammett.core import Screen
from hammett.core.mixins import RouteMixin
from hammett.core.handlers import register_typing_handler


class MyScreen(RouteMixin, Screen):
    @register_typing_handler
    async def process_user_input(self, update, context):
        ...
        return await self.get_return_state_from_routes(update, context)
```

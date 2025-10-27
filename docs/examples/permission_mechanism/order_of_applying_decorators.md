```python
from hammett.core.handlers import register_button_handler
from hammett.core.permission import ignore_permissions


@ignore_permissions([NamePermission])
@register_button_handler
async def handle_something(self, update, context):
    ...
```

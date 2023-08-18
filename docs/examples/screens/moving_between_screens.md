```python
from hammett.core import Button, Screen
from hammett.core.constants import SourceTypes


class First(Screen):
    description = 'This is the first screen'

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                'Next ➡️',
                Second,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )
        ]]

class Second(Screen):
    description = 'This is the second screen'

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                'Back ↩️',
                First,
                source_type=SourceTypes.JUMP_SOURCE_TYPE,
            )
        ]]
```

```python
from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.utils.translation import gettext as _


async def add_default_keyboard(self, update, context):
    language_code = await self.get_language_code(update, context)
    return [
        [
            Button(_('Main menu', language_code),
                   MainMenu,
                   source_type=SourceTypes.MOVE_SOURCE_TYPE),
        ],
    ]
```

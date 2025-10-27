```python
from hammett.core import Screen
from hammett.core.constants import RenderConfig
from telegram import InputMediaDocument
from telegram.constants import ParseMode


class MainMenu(Screen):
    async def get_config(self, _update, _context, **_kwargs):
        return RenderConfig(
            attachments=[
                InputMediaDocument(media=b'123', parse_mode=ParseMode.HTML),
                InputMediaDocument(media=b'123', parse_mode=ParseMode.HTML),
                InputMediaDocument(media=b'123', parse_mode=ParseMode.HTML),
            ],
        )
```

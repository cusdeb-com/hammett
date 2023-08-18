```python
from hammett.core import Screen
from hammett.core.constants import DEFAULT_STATE
from hammett.core.mixins import StartMixin
from hammett.start_marker import StartMarker


class MainMenu(StartMixin, Screen):
    async def start(self, update, context):
        if update.message is None:
            return DEFAULT_STATE

        start_marker = StartMarker(update.message.text)
        start_marker['source']  # содержит 'instory'
        ...
```

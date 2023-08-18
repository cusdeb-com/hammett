```python
from hammett.core import Button
from hammett.core.constants import SourceTypes
from hammett.core.mixins import StartMixin


class AnonymousScreen(StartMixin):
    async def add_default_keyboard(self, _update, _context):
        return [[Button(
            'Introduce Yourself',
            IntroductionScreen,
            source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
        )]]
```

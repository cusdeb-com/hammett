```python
from hammett.conf import settings
from hammett.core import Screen


class MainMenu(Screen):
    cover = settings.MEDIA_ROOT / 'assets' / 'images' / 'cover.jpg'
```

```python
from hammett.core import Screen


class MyScreen(Screen):
 async def get_cover(self, update, context, **kwargs):
     return 'https://some/url/path/to/image.jpg'


 async def get_description(self, update, context, **kwargs):
     return 'This is the description'
```

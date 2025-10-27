```python
from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes


config = RenderConfig()
config.description = 'Your description'
config.keyboard = [[
    Button(
        'Your button',
        'https://github.com/cusdeb-com/hammett',
        source_type=SourceTypes.URL_SOURCE_TYPE,
    ),
]]
```

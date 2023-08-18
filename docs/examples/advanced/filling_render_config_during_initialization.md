```python
from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes

config = RenderConfig(
   description='Your description',
   keyboard=[[
       Button(
           'Your button',
           'https://github.com/cusdeb-com/hammett',
           source_type=SourceTypes.URL_SOURCE_TYPE,
       ),
   ]]
)
```

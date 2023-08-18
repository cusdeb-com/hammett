```python
from hammett.core import Button
from hammett.core.constants import SourceTypes


Button('To my screen', MyScreen,
       source_type=SourceTypes.MOVE_SOURCE_TYPE,
       payload='This is my payload.')
```

```python
from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE


Bot(
    'name',
    entry_point=FirstScreen,
    states={
        DEFAULT_STATE: {FirstScreen, SecondScreen},
    },
)
```

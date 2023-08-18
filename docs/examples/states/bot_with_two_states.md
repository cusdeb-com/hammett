```python
from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE


Bot(
    # There might be some other attributes here
    states={
        DEFAULT_STATE: {MyScreen, ...},
        YET_ANOTHER_STATE: {MyScreen, ...},
    },
)
```

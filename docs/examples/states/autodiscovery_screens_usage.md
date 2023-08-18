```python
from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE
from hammett.utils.autodiscovery import autodiscover_screens


Bot(
     # There might be some other attributes here
    states={
        DEFAULT_STATE: (
            *autodiscover_screens('my_bot.screens', (
                ExcludedScreenOne,
                ExcludedScreenTwo,
            )),
        ),
        YET_ANOTHER_STATE: {ExcludedScreenOne, ExcludedScreenTwo},
    },
)
```

```python
from hammett.core import Bot
from hammett.core.persistence import RedisPersistence


Bot(
    # There might be some other attributes here
    persistence=RedisPersistence(),
)
```

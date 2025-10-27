```python
import sentry_sdk

from hammett.conf import settings


if settings.SENTRY_DSN:
    sentry_sdk.init(
        settings.SENTRY_DSN,
        traces_sample_rate=0.5,
   )
```

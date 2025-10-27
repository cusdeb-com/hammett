```python
from hammett.core import Bot


Bot(
    # There might be some other attributes here
    job_configs=[
        {
            'callback': send_message_per_hour,
            'job_kwargs': {
                'trigger': 'interval',
                'seconds': 60 * 60,
            },
        },
    ],
)
```

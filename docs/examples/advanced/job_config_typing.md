```python
from typing import Any, TypedDict
from telegram._utils.types import JSONDict
from telegram.ext import CallbackContext
from telegram.ext._utils.types import JobCallback


class JobConfig(TypedDict):
    callback: JobCallback[CallbackContext[Any, Any, Any, Any]]
    job_kwargs: JSONDict
```

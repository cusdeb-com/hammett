```python
from collections.abc import Sequence
import telegram


Attachments = (
    Sequence[telegram.InputMediaAudio] | Sequence[telegram.InputMediaDocument] |
    Sequence[telegram.InputMediaPhoto] | Sequence[telegram.InputMediaVideo]
)
```

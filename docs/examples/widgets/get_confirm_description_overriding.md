```python
from datetime import datetime, timezone

from hammett.widgets import CalendarWidget


class Calendar(CalendarWidget):
    async def get_confirm_description(self, update, context, result_date):
        return f"You've scheduled the meeting on {result_date.strftime('%d %B, %Y')}"
```

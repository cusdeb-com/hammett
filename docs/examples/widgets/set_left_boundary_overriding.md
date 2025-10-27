```python
from datetime import datetime, timezone

from hammett.widgets import CalendarWidget
from hammett.widgets.calendar_widget import CalendarUnit


class Calendar(CalendarWidget):
    initial_unit = CalendarUnit.MONTH

    async def set_left_boundary(self, _update, _context):
        return datetime.now(tz=timezone.utc).date()
```

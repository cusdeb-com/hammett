```python
from datetime import datetime, timezone

from hammett.widgets import CalendarWidget


class Calendar(CalendarWidget):
   async def get_month_description(self, _update, _context, current_date):
       return f'Choose a month in the {current_date.year} year.'
```

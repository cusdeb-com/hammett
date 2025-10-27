```python
import json
from datetime import datetime, timezone

from hammett.core.handlers import register_button_handler
from hammett.widgets import CalendarWidget


class Calendar(CalendarWidget):
   @register_button_handler
   async def on_day_click(self, update, context):
       payload = json.loads(await self.get_payload(update, context))
       context.user_data['date'] = payload['date']  # save payload for further processing
       return await AnotherScreen().move(update, context)
```

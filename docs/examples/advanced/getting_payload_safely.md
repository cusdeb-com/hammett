```python
from hammett.core.constants import DEFAULT_STATE, RenderConfig
from hammett.core.exceptions import FailedToGetDataAttributeOfQuery, PayloadIsEmpty
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin

MY_PAYLOAD_KEY = 'my_payload_key'


class MainMenuScreen(StartMixin):
   async def get_payload_safely(self, update, context, key):
       try:
           payload = await self.get_payload(update, context)
       except (FailedToGetDataAttributeOfQuery, PayloadIsEmpty):
           try:
               payload = context.user_data[key]
           except KeyError:
               raise
       else:
           context.user_data[key] = payload

       return payload

   @register_button_handler
   async def handle_button_click(self, update, context):
       payload = await self.get_payload_safely(update, context, MY_PAYLOAD_KEY)

       await self.render(update, context, config=RenderConfig(description=payload))
       return DEFAULT_STATE
```

```python
from hammett.core import Button, Screen
from hammett.core.constants import SourceTypes
from hammett.core.handlers import register_button_handler


class Clicker(Screen):
    async def add_default_keyboard(self, update, context):
        return [[
            Button(
                'Press to add one point',
                self.add_one_click,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            ),
        ]]

    @register_button_handler
    async def add_one_click(self, update, context):
        context.user_data['num_of_tab'] += 1
        return await self.move(update, context)


    async def get_description(self, update, context):
        return f"You've pressed <b>{context.user_data.get('num_of_tab', 0)}</b> times"
```

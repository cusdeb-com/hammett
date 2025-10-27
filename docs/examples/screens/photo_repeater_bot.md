```python
from hammett.core import Screen
from hammett.core.handlers import register_input_handler
from hammett.core.mixins import StartMixin
from telegram.ext import filters


class MyScreen(StartMixin, Screen):
    description = 'Your description'

    async def get_cover(self, update, context):
        if context.user_data.get('photo'):
            return context.user_data['photo']

        return await super().get_cover(update, context)


    @register_input_handler(filters=filters.PHOTO)
    async def handle_photo_input(self, update, context):
        context.user_data['photo'] = update.message.photo[-1]

        return await self.jump(update, context)
```

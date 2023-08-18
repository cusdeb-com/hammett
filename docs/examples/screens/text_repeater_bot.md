```python
from hammett.core import Screen
from hammett.core.handlers import register_typing_handler


class MeScreen(Screen):
    async def get_description(self, update, context):
        if context.user_data.get('text_input'):
            return (
                f'This is your input:\n'
                f'\n'
                f'{context.user_data["text_input"]}'
            )

        return 'Hey! Try to type something and I will send it back to you!'

    @register_typing_handler
    async def handle_text_input(self, update, context):
        context.user_data['text_input'] = update.message.text

        return await self.jump(update, context)
```

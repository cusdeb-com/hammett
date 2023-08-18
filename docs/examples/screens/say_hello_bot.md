```python
from hammett.core import Screen
from hammett.core.handlers import register_command_handler
from hammett.core.mixins import StartMixin


class StartScreen(StartMixin):
    description = 'This text is sent as a response to the /start command.'


class SayingHi(Screen):
    description = 'This text is sent as a response to the /say_hello command.'

    @register_command_handler('say_hello')
    async def handle_typing_say_hello_command(self, update, context):
        return await self.jump(update, context)
```

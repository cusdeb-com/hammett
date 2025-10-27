```python title="bot.py"
from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.mixins import StartMixin


class Main(StartMixin, Screen):
    description = 'Hello, World!'

    async def add_default_keyboard(self, update, context):
        return [[
            Button('🎸 Hello, World!', 'https://github.com/cusdeb-com/hammett',
                   source_type=SourceTypes.URL_SOURCE_TYPE),
        ]]

def main():
    name = 'HelloWorld'
    app = Bot(
        name,
        entry_point=Main,
        states={
            DEFAULT_STATE: {Main},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
```

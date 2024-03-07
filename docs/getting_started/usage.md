# Usage

The simplest example using Hammett:

``` py title="bot.py" linenums="1"
from hammett.core import Application
from hammett.core.screen import Button, RenderConfig, StartScreen
from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.utils.autodiscovery import autodiscover_screens

class MainMenu(StartScreen):
    def setup_keyboard(self):
        return [
            [
                Button('🎸 Hello, World!', 'https://github.com/cusdeb-com/hammett',
                       source_type=SourcesTypes.URL_SOURCE_TYPE),
            ],
        ]

    def start(self, update, context):
        config = RenderConfig(as_new_message=True)
        await self.render(update, context, config=config)
        return DEFAULT_STAGE

def main(): 
    name = 'demo'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STAGE: autodiscover_screens('bot'),
        },
    )
    app.run()
```

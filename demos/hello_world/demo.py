from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.mixins import StartMixin
from hammett.core.screen import Screen


class HelloScreen(StartMixin, Screen):
    description = 'Hello, World!'

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                'Next screen ➡️',
                YetAnotherScreen,
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
            )
        ]]


class YetAnotherScreen(StartMixin, Screen):
    description = (
        'This is just another screen to demonstrate the built-in '
        'capability to switch between screens.'
    )

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                '⬅️ Back',
                HelloScreen,
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
            )
        ]]


def main():
    """Runs the bot."""

    name = 'hello_world'
    app = Application(
        name,
        entry_point=HelloScreen,
        states={
            DEFAULT_STATE: [HelloScreen, YetAnotherScreen],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

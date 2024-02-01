from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.screen import StartScreen


class HelloScreen(StartScreen):
    description = 'Hello, World!'

    def setup_keyboard(self):
        return [[
            Button(
                'Next screen ➡️',
                YetAnotherScreen,
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
            )
        ]]


class YetAnotherScreen(StartScreen):
    description = (
        'This is just another screen to demonstrate the built-in '
        'capability to switch between screens.'
    )

    def setup_keyboard(self):
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

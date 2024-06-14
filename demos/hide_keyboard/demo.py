"""The bot is designed to demonstrate how to hide the keyboard in previous messages."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.screen import StartScreen


class MainScreen(StartScreen):
    description = 'This message will drop the keyboard after going to the next screen'
    hide_keyboard = True

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                'Next screen ➡️',
                NextScreen,
                source_type=SourcesTypes.JUMP_SOURCE_TYPE,
            )
        ]]


class NextScreen(StartScreen):
    description = (
        "It's magic! This screen won't have a lost keyboard because it has "
        "hide_keyboard is False.\n"
        "\n"
        "You can try again by going back to the previous screen."
    )

    async def add_default_keyboard(self, _update, _context):
        return [[
            Button(
                '⬅️ Back',
                MainScreen,
                source_type=SourcesTypes.JUMP_SOURCE_TYPE,
            )
        ]]


def main():
    """Runs the bot."""

    name = 'hide_keyboard'
    app = Application(
        name,
        entry_point=MainScreen,
        states={
            DEFAULT_STATE: [MainScreen, NextScreen],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

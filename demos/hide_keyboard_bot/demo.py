"""The module is a script for running the bot."""

from hammett.core import Application, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

NEXT_SCREEN_DESCRIPTION = (
    'The previous screen has <b>hidden</b> its keyboard! '
    'The same will happen with this screen as well. Give it a try!'
)

START_SCREEN_DESCRIPTION = (
    'Welcome to HammettHideKeyboardBot!\n'
    '\n'
    '<i>This screen will <b>hide</b> the keyboard right after jumping '
    'to the next screen.</i>'
)


class BaseScreen(Screen):
    """The base screen for all the screens in the bot."""

    hide_keyboard = True


class NextScreen(BaseScreen):
    """The class implements NextScreen."""

    description = NEXT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '⬅️ Back',
                StartScreen,
                source_type=SourceTypes.JUMP_SOURCE_TYPE,
            ),
        ]]


class StartScreen(BaseScreen, StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                'Next screen ➡️',
                NextScreen,
                source_type=SourceTypes.JUMP_SOURCE_TYPE,
            )],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/hide_keyboard_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]


def main():
    """Run the bot."""
    app = Application(
        'HammettHideKeyboardBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {NextScreen, StartScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()

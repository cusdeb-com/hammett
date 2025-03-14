"""The module is a script for running the bot."""

from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.handlers import register_command_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

HELLO_SCREEN_DESCRIPTION = (
    'Hello 👋\n'
    'Now you see <b>HelloScreen</b>.'
)

START_SCREEN_DESCRIPTION = (
    'Welcome to HammettSimpleJumpBot!\n'
    '\n'
    'This is <b>StartScreen</b>, which acts as a response to the /start command. '
    'Now execute the /say_hello command, please.'
)


class HelloScreen(Screen):
    """The class implements HelloScreen, which acts as a response
    to the /say_hello command.
    """

    description = HELLO_SCREEN_DESCRIPTION

    @register_command_handler('say_hello')
    async def handle_typing_say_hello_command(self, update, context):
        """Send HelloScreen as a response to the /say_hello command."""
        return await self.jump(update, context)


class StartScreen(StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/say_hello_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]


def main():
    """Run the bot."""
    bot = Bot(
        'HammettSayHelloBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {HelloScreen, StartScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

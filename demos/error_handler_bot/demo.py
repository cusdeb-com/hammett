"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

from error_handler import custom_error_handler
from exeptions import CustomError

ERROR_HANDLING_EXAMPLES_DESCRIPTION = (
    'Each button below intentionally raises a specific exception.\n'
    '\n'
    'This allows you to see how different error scenarios are processed:\n'
    '• handled automatically\n'
    '• handled by custom error logic\n'
    '• or treated as an unexpected exception.\n'
    '\n'
    'Pay attention to both the bot response and the log output '
    'to understand how each case is handled.'
)

START_SCREEN_DESCRIPTION = (
    'Welcome to HammettErrorHandlerBot! 👋\n'
    '\n'
    'This demo allows you to explore how error handlers react '
    'to different failure scenarios.\n'
    '\n'
    'You can trigger several types of exceptions and observe '
    'how they are handled from both the user interface and the logs.'
)


class StartScreen(StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '🧪 Error handling examples',
                ErrorHandlingExamples,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/error_handler_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )],
        ]


class ErrorHandlingExamples(Screen):
    """The class implements ErrorHandlingExamples."""

    description = ERROR_HANDLING_EXAMPLES_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '✏️ MessageNotModified — handled by framework',
                self.__class__,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                '⚠️ CustomError — handled by custom logic',
                self.raise_custom_error,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            )],
            [Button(
                '🔑 KeyError — unexpected',
                self.raise_key_error,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            )],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/error_handler_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )],
        ]

    @register_button_handler
    async def raise_custom_error(self, _update, _context):
        """Trigger an error to demonstrate error handling."""
        raise CustomError

    @register_button_handler
    async def raise_key_error(self, _update, _context):
        """Trigger an error to demonstrate error handling."""
        raise KeyError


def main():
    """Run the bot."""
    bot = Bot(
        'HammettErrorHandlerBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        error_handlers=[custom_error_handler],
        states={
            DEFAULT_STATE: {ErrorHandlingExamples, StartScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

"""The module is a script for running the bot."""

import aiofiles
from telegram import InputMediaDocument

from hammett.conf import settings
from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.core.handlers import register_command_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

START_SCREEN_DESCRIPTION = (
    'Welcome to <b>HammettAttachmentsBot</b>! 🎨\n'
    '\n'
    'This demo showcases how to send multiple document attachments '
    'using the <code>RenderConfig</code> with the <code>attachments</code> attribute.\n'
    '\n'
    'Use the /attachments command to see the logo collection 👇'
)


class AttachmentsScreen(Screen):
    """The class implements AttachmentsScreen, demonstrating multiple document attachments."""

    @staticmethod
    async def _read_file(filename):
        """Read and return data from a file."""
        async with aiofiles.open(settings.MEDIA_ROOT / filename, 'rb') as file:
            return await file.read()

    async def get_config(self, _update, _context, **_kwargs):
        """Return the Screen's config."""
        logos = [
            ('logo-1500px.png', '📄 Big Hammett Logo (1500x1500 px)'),
            ('logo-500px.png', '📄 Medium Hammett Logo (500x500 px)'),
            ('logo-200px.png', '📄 Small Hammett Logo (200x200 px)'),
        ]
        documents = [
            {
                'filename': filename,
                'caption': caption,
                'media': await self._read_file(filename),
            } for filename, caption in logos
        ]

        return RenderConfig(attachments=[
            InputMediaDocument(**document) for document in documents
        ])


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
                'https://github.com/cusdeb-com/hammett/tree/main/demos/attachments_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]

    @register_command_handler('attachments')
    async def handle_attachments_command(self, update, context):
        """Send AttachmentsScreen as a response to the /attachments command."""
        return await AttachmentsScreen().jump(update, context)


def main():
    """Run the bot."""
    bot = Bot(
        'HammettAttachmentsBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {AttachmentsScreen, StartScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

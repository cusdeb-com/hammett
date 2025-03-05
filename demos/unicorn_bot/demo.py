"""The module is a script for running the bot."""

from io import BytesIO

from PIL import Image
from telegram import InputMediaPhoto

from hammett.conf import settings
from hammett.core import Application, Screen, Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.handlers import register_input_handler
from hammett.core.mixins import StartMixin, RouteMixin
from hammett.core.persistence import RedisPersistence
from telegram.ext import filters

from hammett.types import State

ADDING_UNICORN_SCREEN_DESCRIPTION = (
    'Send a photo to add to it a unicorn.'
)

MAIN_MENU_SCREEN_DESCRIPTION = (
    'Welcome to HammettUnicornBot!\n'
    '\n'
    'Let magic happen!'
)

UNICORN_STATE = State('unicorn')


class MainMenuScreen(StartMixin, Screen):
    """The class implements MainMenuScreen."""

    description =  MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, update, context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                'Send a photo!',
                AddingUnicornScreen,
                source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
            ),
        ]]

    async def start(self, update, context):
        """Handle the /start command and save the image to be pasted."""
        context.user_data['unicorn'] = Image.open(settings.MEDIA_ROOT / 'unicorn.png')

        return await super().start(update, context)

class AddingUnicornScreen(RouteMixin, Screen):
    """The class implements AddingUnicornScreen."""

    description = ADDING_UNICORN_SCREEN_DESCRIPTION
    routes = (
        ({DEFAULT_STATE}, UNICORN_STATE),
    )

    async def get_cover(self, update, context):
        if context.user_data.get('photo'):
            return InputMediaPhoto(media=context.user_data['photo'].read())

        return await super().get_cover(update, context)

    @register_input_handler(filters=filters.PHOTO)
    async def handle_photo_input(self, update, context):
        """Process an input of photo from the user."""
        file = await update.message.photo[-1].get_file()
        bytearray_ = await file.download_as_bytearray()
        img = Image.open(BytesIO(bytearray_))

        img.paste(context.user_data['unicorn'], (0, 0))

        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        context.user_data['photo'] = output

        return await self.jump(update, context)


def main():
    """Run the bot."""
    app = Application(
        'HammettUnicornBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {MainMenuScreen},
            UNICORN_STATE: {AddingUnicornScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()

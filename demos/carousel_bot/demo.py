"""The module is a script for running the bot."""

from hammett.conf import settings
from hammett.core import Bot, Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence
from hammett.widgets import CarouselWidget

MAIN_MENU_SCREEN_FIRST_DESCRIPTION = (
    'Welcome to HammettCarouselBot!\n'
    '\n'
    'This is the first image in the carousel. To see the next one or '
    'go back to the previous one, use the navigation buttons below 👇'
)

MAIN_MENU_SCREEN_LAST_DESCRIPTION = (
    "This is the end of the carousel.\n"
    "\n"
    "Don't forget to check out Hammett and the source code of the demo!"
)

MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION = (
    'Take part in open source and become a superhero 🕷🕸 in software development!'
)


class Gallery(CarouselWidget, StartMixin):
    """The class implements the gallery screen."""

    cache_covers = True
    images = [
        [settings.MEDIA_ROOT / '01.png', MAIN_MENU_SCREEN_FIRST_DESCRIPTION],
        [settings.MEDIA_ROOT / '02.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '03.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '04.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '05.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '06.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '07.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '08.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '09.png', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '10.png', MAIN_MENU_SCREEN_LAST_DESCRIPTION],
    ]

    async def add_extra_keyboard(self, _update, _context):
        """Return extra keyboard below the widget buttons."""
        return [
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/carousel_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]


def main():
    """Run the bot."""
    bot = Bot(
        'HammettCarouselBot',
        entry_point=Gallery,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {Gallery},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

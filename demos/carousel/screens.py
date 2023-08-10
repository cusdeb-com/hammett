"""The module contains the screens the bot consists of. """

from hammett.conf import settings
from hammett.widgets import CarouselWidget


class MainMenu(CarouselWidget):
    cache_covers = True
    caption = 'Take part in Open Source and become a superhero🕷🕸 in software development!'
    homepage = "Here's the Hammett homepage: https://github.com/cusdeb-com/hammett"
    images = [
        [settings.MEDIA_ROOT / '01.jpg', caption],
        [settings.MEDIA_ROOT / '02.jpg', caption],
        [settings.MEDIA_ROOT / '03.jpg', caption],
        [settings.MEDIA_ROOT / '04.jpg', caption],
        [settings.MEDIA_ROOT / '05.jpg', caption],
        [settings.MEDIA_ROOT / '06.jpg', caption],
        [settings.MEDIA_ROOT / '07.jpg', caption],
        [settings.MEDIA_ROOT / '08.jpg', caption],
        [settings.MEDIA_ROOT / '09.jpg', caption],
        [settings.MEDIA_ROOT / '10.jpg', homepage],
    ]

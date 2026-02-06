"""The module is a script for running the bot."""

import json

import aiofiles

from hammett.conf import settings
from hammett.core import Bot, Button
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence
from hammett.template import render_template_from_string

START_SCREEN_TEMPLATE = (
    'Welcome to <b>HammettJinja2Bot</b>! 🎨\n'
    '\n'
    'This demo shows how to use <b>Jinja2 templates</b> for dynamic descriptions. '
    'It uses a <b>for loop</b> to render a list of demos below. '
    'You can explore more features in the '
    '<a href="https://jinja.palletsprojects.com/">Jinja2 documentation</a>.\n'
    '\n'
    '<b>Live Demos:</b>\n'
    '{% for demo in demos %}'
    '{{ loop.index }}. <a href="{{ demo.url }}">{{ demo.name }}</a>\n'
    '{% endfor %}'
)


class StartScreen(StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/jinja2_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]

    async def get_description(self, _update, context):
        """Return the description with rendered list of demos."""
        return render_template_from_string(
            START_SCREEN_TEMPLATE,
            {'demos': context.user_data['demos']},
        )

    async def start(self, update, context):
        """Reply to the /start command, load and save the questions from the file."""
        async with aiofiles.open(settings.BASE_DIR / 'demos.json') as file:
            demos = json.loads(await file.read())
            context.user_data['demos'] = demos

        return await super().start(update, context)


def main():
    """Run the bot."""
    bot = Bot(
        'HammettJinja2Bot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {StartScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

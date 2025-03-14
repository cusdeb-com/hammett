"""The module is a script for running the bot."""

from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.mixins import RouteMixin, StartMixin
from hammett.core.persistence import RedisPersistence

ANONYMOUS_SCREEN_DESCRIPTION = (
    'Hello, <b>Anonymous</b>!\n'
    '\n'
    '<i>The bot is in the <b>DEFAULT</b> state now</i>.'
)

INTRODUCTION_SCREEN_WITH_NAME_DESCRIPTION = (
    'Hi, <b>{name}</b>!\n'
    '\n'
    '<i>The bot has switched back to the <b>DEFAULT</b> state</i>.'
)

INTRODUCTION_SCREEN_WITHOUT_NAME_DESCRIPTION = (
    "What's your name?\n"
    "\n"
    "<i>The bot is now switched to the <b>TYPE_NAME</b> state</i>."
)

TYPE_NAME_STATE = 'type_name_state'


class AnonymousScreen(StartMixin):
    """The class implements AnonymousScreen. It will be registered
    in DEFAULT_STATE.
    """

    description = ANONYMOUS_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [
            [Button(
                'Introduce Yourself',
                IntroductionScreen,
                source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
            )],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/multi_state_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]


class IntroductionScreen(RouteMixin, Screen):
    """The class implements IntroductionScreen. It will be registered
    in TYPE_NAME_STATE.
    """

    routes = (
        ({DEFAULT_STATE}, TYPE_NAME_STATE),
    )

    description = INTRODUCTION_SCREEN_WITHOUT_NAME_DESCRIPTION

    @register_typing_handler
    async def handle_text_input(self, update, context):
        """Handle a text input and return DEFAULT_STATE."""
        await self.render(update, context, config=RenderConfig(
            as_new_message=True,
            description=INTRODUCTION_SCREEN_WITH_NAME_DESCRIPTION.format(name=update.message.text),
            keyboard=[
                [Button(
                    'Change Name',
                    IntroductionScreen,
                    source_type=SourceTypes.MOVE_ALONG_ROUTE_SOURCE_TYPE,
                )],
                [Button(
                    '📄 Source Code',
                    'https://github.com/cusdeb-com/hammett/tree/main/demos/multi_state_bot',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button(
                    '🎸 Hammett Homepage',
                    'https://github.com/cusdeb-com/hammett',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
                ],
        ))
        return DEFAULT_STATE


def main():
    """Run the bot."""
    bot = Bot(
        'HammettMultiStateBot',
        entry_point=AnonymousScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {AnonymousScreen},
            TYPE_NAME_STATE: {IntroductionScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

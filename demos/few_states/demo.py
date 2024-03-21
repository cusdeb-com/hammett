"""The bot is designed to demonstrate how to work with multiple states."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourcesTypes
from hammett.core.handlers import register_typing_handler
from hammett.core.screen import RouteMixin, Screen, StartScreen

ANOTHER_STATE = 'another_state'


class MainMenu(StartScreen):
    """The screen that will be registered in the DEFAULT_STATE."""

    description = (
        'This is the screen that is registered in DEFAULT_STATE\n'
        '\n'
        'In this state the text input handler will not work, you can try to write something. '
        'Spoiler: nothing will happen'
    )

    def setup_keyboard(self):
        """Sets up the keyboard for the screen."""

        return [[
            Button(
                'Move to another state',
                AnotherScreen,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
            )
        ]]


class AnotherScreen(RouteMixin, Screen):
    """The screen that will be registered in the ANOTHER_STATE."""

    routes = (
        ({DEFAULT_STATE}, ANOTHER_STATE),
    )

    description = (
        'This is the screen that is registered in ANOTHER_STATE.\n'
        '\n'
        'Write something here, the text input handler will be called and return to the '
        'previous state.'
    )

    @register_typing_handler
    async def handle_text_input(self, update, context):
        """Handles text input and returns to DEFAULT_STATE."""

        text = update.message.text
        keyboard = [[
            Button(
                'Try again',
                AnotherScreen,
                source_type=SourcesTypes.SGOTO_SOURCE_TYPE,
            )
        ]]

        config = RenderConfig(
            as_new_message=True,
            description=f"Hi, {text}, I'm Dad!",
            keyboard=keyboard,
        )
        await self.render(update, context, config=config)
        return DEFAULT_STATE


def main():
    """Runs the bot."""

    name = 'few_states'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: [MainMenu],
            ANOTHER_STATE: [AnotherScreen]
        },
    )
    app.run()


if __name__ == '__main__':
    main()

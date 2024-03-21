"""The bot is intended to demonstrate how to create and work with a dynamic keyboard."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.screen import StartScreen


async def request_dynamic_keyboard(handler):
    """Emulates an API request, passes a payload and returns the keyboard."""

    buttons = range(3)  # do some API request

    return [
        [Button(
            f'Button {button_num + 1}',
            handler,
            source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            payload=f"You pressed button number {button_num + 1}, I'm right?"
        )]
        for button_num in buttons
    ]


class MainMenu(StartScreen):
    description = 'Just press any button'

    async def get_config(self, update, context, **kwargs):
        """Returns the Screen's config."""

        keyboard = await request_dynamic_keyboard(self.handle_button_click)
        return RenderConfig(keyboard=keyboard)

    @register_button_handler
    async def handle_button_click(self, update, context):
        """Handles a button click and renders payload text."""

        payload = await self.get_payload(update, context)
        keyboard = await request_dynamic_keyboard(self.handle_button_click)

        config = RenderConfig(description=payload, keyboard=keyboard)
        await self.render(update, context, config=config)

        return DEFAULT_STATE


def main():
    """Runs the bot. """

    name = 'dynamic_keyboard'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: [MainMenu],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

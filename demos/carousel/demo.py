"""The bot is designed to demonstrate how to use the carousel widget."""

from hammett.core import Application
from hammett.core.screen import DEFAULT_STAGE

from demos.carousel.screens import MainMenu


def main():
    """Runs the bot. """

    name = 'carousel'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STAGE: [MainMenu],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

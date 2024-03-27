"""The bot is designed to demonstrate how to use the multichoice widget."""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE

from demos.multi_choices.screens import MainMenu


def main():
    """Runs the bot."""

    name = 'multi_choices'
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

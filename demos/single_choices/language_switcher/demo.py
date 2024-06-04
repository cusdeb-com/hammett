"""The bot is designed to demonstrate how to use the single choice widget."""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE

from demos.single_choices.language_switcher.screens import MainMenu


def main():
    """Runs the bot."""

    name = 'language_switcher'
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

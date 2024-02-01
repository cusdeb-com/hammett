"""The bot is intended to demonstrate how to use the hiders mechanism
to control the visibility of the buttons on the screens.
"""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE
from hammett.utils.autodiscovery import autodiscover_screens

from demos.hiders.screens import MainMenu


def main():
    """Runs the bot. """

    name = 'hiders'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: autodiscover_screens('demos.hiders'),
        },
    )
    app.run()


if __name__ == '__main__':
    main()

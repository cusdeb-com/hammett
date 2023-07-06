"""The bot is intended to demonstrate how to use the hiders mechanism
to control the visibility of the buttons on the screens.
"""

from demos.screens import (
    MainMenu,
    NotAdminConfirmation,
    SecretRoom,
)
from hammett.core import Application
from hammett.core.screen import DEFAULT_STAGE


def main():
    """Runs the bot. """

    name = 'demo'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STAGE: [
                MainMenu,
                NotAdminConfirmation,
                SecretRoom,
            ],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

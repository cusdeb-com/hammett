"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE
from hammett.core.persistence import RedisPersistence

from screens import AdminPanelScreen, MainMenuScreen, NotAdminConfirmationScreen


def main():
    """Run the bot."""
    app = Application(
        'HammettAdminPanelBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {AdminPanelScreen, MainMenuScreen, NotAdminConfirmationScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()

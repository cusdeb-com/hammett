"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE
from hammett.core.persistence import RedisPersistence

from screens import MainMenuScreen, ReminderScreen, SettingReminderScreen


def main():
    """Run the bot."""
    bot = Bot(
        'HammettReminderBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {MainMenuScreen, ReminderScreen, SettingReminderScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

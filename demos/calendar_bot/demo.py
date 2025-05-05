"""The module is a script for running the bot."""

from datetime import datetime, timezone

from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence
from hammett.widgets import CalendarWidget

CHOOSING_DATE_SCREEN_TEMPLATE = (
    'Calculations have just been completed.\n'
    '\n'
    'There are <b>{days}</b> days left until <i>{day} {month} {year}</i>!'
)

MAIN_MENU_SCREEN_DESCRIPTION = (
    'Welcome to HammettCalendarBot!\n'
    '\n'
    'You can pick any date, and the bot will tell you '
    'how many days are left until then.'
)


def _calculate_days(date_):
    """Return the number of days remaining until the selected date."""
    return (date_ - datetime.now(tz=timezone.utc).date()).days


class ChoosingDateScreen(CalendarWidget):
    """The class implements ChoosingDateScreen."""

    async def add_extra_keyboard(self, _update, _context):
        """Add an extra keyboard below the widget buttons."""
        return [
            [Button(
                '🏠 Main Menu',
                MainMenuScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE)],
        ]

    async def get_confirm_description(self, update, context, result_date):
        """Return the widget description for the selected date."""
        return CHOOSING_DATE_SCREEN_TEMPLATE.format(
            days=_calculate_days(result_date),
            year=result_date.year,
            month=self.get_month_name(
                result_date.month,
                await self.get_language_code(update, context),
            ),
            day=result_date.day,
        )

    async def set_left_boundary(self, _update, _context):
        """Return the earliest date that can be selected in the calendar."""
        return datetime.now(tz=timezone.utc).date()


class MainMenuScreen(StartMixin, Screen):
    """The class implements MainMenuScreen, which acts as a response
    to the /start command.
    """

    description = MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '🗓 Choose Date',
                ChoosingDateScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE)],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/calendar_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]


def main():
    """Run the bot."""
    bot = Bot(
        'HammettCalendarBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {ChoosingDateScreen, MainMenuScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

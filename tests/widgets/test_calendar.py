"""The module contains the tests for CalendarWidget."""

# ruff: noqa: SLF001

from datetime import datetime, timezone

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from hammett.widgets.calendar_widget import (
    CalendarUnit,
    CalendarWidget,
    _arrange_buttons_into_rows,
    _get_left_boundary,
    _get_right_boundary,
)


class TestDayCalendarWidget(CalendarWidget):
    """The class implements a calendar widget with `CalendarUnit.day`
    as the initial unit.
    """

    initial_unit = CalendarUnit.DAY


class TestMonthCalendarWidget(CalendarWidget):
    """The class implements a calendar widget with `CalendarUnit.month`
    as the initial unit.
    """

    initial_unit = CalendarUnit.MONTH


class TestYearCalendarWidget(CalendarWidget):
    """The class implements a calendar widget with `CalendarUnit.year`
    as the initial unit.
    """


class CalendarWidgetTests(BaseTestCase):
    """The class implements the tests for CalendarWidget."""

    @catch_render_config()
    async def test_calendar_render_after_calling_do_nothing_handler(self, actual):
        """Test getting the calendar config using the `_do_nothing` handler."""
        await TestDayCalendarWidget()._do_nothing(self.update, self.context)

        self.assertIsNone(actual.final_render_config)

    @catch_render_config()
    async def test_day_calendar_page_render_after_calling_send_handler(self, actual):
        """Test getting the day calendar page using the `send` handler."""
        await TestDayCalendarWidget().send(self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=TestDayCalendarWidget.day_description,
            keyboard=[
                *await TestDayCalendarWidget()._build_days(self.update, self.context, None),
                *await TestDayCalendarWidget().add_extra_keyboard(self.update, self.context),
            ],
        ))
        self.assertEqual(actual.final_render_config, expected)

    async def test_getting_arranged_buttons(self):
        """Test getting the arranged buttons."""
        buttons = [
            Button('1', 'test', source_type=SourceTypes.URL_SOURCE_TYPE),
            Button('2', 'test', source_type=SourceTypes.URL_SOURCE_TYPE),
            Button('3', 'test', source_type=SourceTypes.URL_SOURCE_TYPE),
            Button('4', 'test', source_type=SourceTypes.URL_SOURCE_TYPE),
        ]

        row_size = 2
        arranged_buttons = _arrange_buttons_into_rows(buttons, row_size=row_size)
        self.assertEqual(len(arranged_buttons[0]), row_size)
        self.assertEqual(len(arranged_buttons[1]), row_size)

    async def test_getting_calendar_description_that_includes_result_date(self):
        """Test getting the description that includes the result date."""
        actual = await TestDayCalendarWidget().get_confirm_description(
            self.update, self.context, datetime(1, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(actual, '1 Jan 1')

    async def test_getting_left_boundary(self):
        """Test getting the left boundary of the given calendar unit."""
        date = datetime(10, 10, 10, tzinfo=timezone.utc).date()

        actual = _get_left_boundary(date, CalendarUnit.DAY)
        self.assertEqual(actual, date)

        actual = _get_left_boundary(date, CalendarUnit.MONTH)
        self.assertEqual(actual, datetime(10, 10, 1, tzinfo=timezone.utc).date())

        actual = _get_left_boundary(date, CalendarUnit.YEAR)
        self.assertEqual(actual, datetime(10, 1, 1, tzinfo=timezone.utc).date())

    async def test_getting_right_boundary(self):
        """Test getting the right boundary of the given calendar unit."""
        date = datetime(10, 10, 10, tzinfo=timezone.utc).date()

        actual = _get_right_boundary(date, CalendarUnit.DAY)
        self.assertEqual(actual, date)

        actual = _get_right_boundary(date, CalendarUnit.MONTH)
        self.assertEqual(actual, datetime(10, 10, 31, tzinfo=timezone.utc).date())

        actual = _get_right_boundary(date, CalendarUnit.YEAR)
        self.assertEqual(actual, datetime(10, 12, 31, tzinfo=timezone.utc).date())

    async def test_getting_month_name(self):
        """Test getting the translated month names."""
        expected = [
            'янв', 'фев', 'мар', 'апр', 'май', 'июн',
            'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
        ]
        self.assertEqual([
            TestDayCalendarWidget.get_month_name(month, 'ru')
            for month in range(1, 13)
        ], expected)

        self.context.user_data.pop('language_code', None)

    @catch_render_config()
    async def test_month_calendar_page_render_after_calling_jump_handler(self, actual):
        """Test getting the month calendar page using the `jump` handler."""
        await TestMonthCalendarWidget().jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=TestMonthCalendarWidget.month_description,
            keyboard=[
                *await TestMonthCalendarWidget()._build_months(self.update, self.context, None),
                *await TestMonthCalendarWidget().add_extra_keyboard(self.update, self.context),
            ],
        ))
        self.assertEqual(actual.final_render_config, expected)

    @catch_render_config()
    async def test_year_calendar_page_render_after_calling_move_handler(self, actual):
        """Test getting the year calendar page using the `move` handler."""
        await TestYearCalendarWidget().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestYearCalendarWidget.year_description,
            keyboard=[
                *await TestYearCalendarWidget()._build_years(self.update, self.context, None),
                *await TestYearCalendarWidget().add_extra_keyboard(self.update, self.context),
            ],
        ))
        self.assertEqual(actual.final_render_config, expected)

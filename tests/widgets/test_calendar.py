"""The module contains the tests for CalendarWidget."""

# ruff: noqa: SLF001

import calendar
import json
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from hammett.core import Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
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


class CalendarWidgetTests(BaseTestCase):  # noqa: PLR0904
    """The class implements the tests for CalendarWidget."""

    @catch_render_config()
    async def test_calendar_render_after_calling_do_nothing_handler(self, actual):
        """Test getting the calendar config using the `_do_nothing` handler."""
        await TestDayCalendarWidget()._do_nothing(self.update, self.context)

        assert actual.final_render_config is None

    @catch_render_config()
    async def test_day_calendar_page_render_after_calling_send_handler(self, actual):
        """Test getting the day calendar page using the `send` handler."""
        await TestDayCalendarWidget().send(self.context)

        expected = self.prepare_final_render_config(
            RenderConfig(
                as_new_message=True,
                description=TestDayCalendarWidget.day_description,
                keyboard=[
                    *await TestDayCalendarWidget()._build_days(self.update, self.context, None),
                    *await TestDayCalendarWidget().add_extra_keyboard(self.update, self.context),
                ],
            ),
        )
        assert actual.final_render_config == expected

    @catch_render_config()
    async def test_day_calendar_render_after_calling_on_day_click_handler(self, actual):
        """Test getting the final render config using the `on_day_click` handler."""
        picked = ['2025', '10', '07']
        data = json.dumps({'date': picked})

        with (
            patch(
                'hammett.core.screen.get_callback_query',
                return_value=SimpleNamespace(message=self.message, data='key'),
            ),
            patch('hammett.core.handlers.get_payload_storage', return_value={'key': data}),
        ):
            widget = TestDayCalendarWidget()
            state = await widget.on_day_click(self.update, self.context)

            picked_date = date(*map(int, picked))
            expected = self.prepare_final_render_config(
                RenderConfig(
                    message_id=self.message_id,
                    description=await widget.get_confirm_description(
                        self.update,
                        self.context,
                        picked_date,
                    ),
                    keyboard=[
                        *await widget.add_extra_keyboard(self.update, self.context),
                    ],
                ),
            )
            assert actual.final_render_config == expected
            assert state == DEFAULT_STATE

    async def test_default_description_getters_return_attributes(self):
        """Test that default description getters return corresponding class attributes."""
        some_date = date(2020, 1, 1)
        widget = TestYearCalendarWidget()
        assert (
            await widget.get_year_description(self.update, self.context, some_date)
            == TestYearCalendarWidget.year_description
        )

        widget = TestMonthCalendarWidget()
        assert (
            await widget.get_month_description(self.update, self.context, some_date)
            == TestMonthCalendarWidget.month_description
        )

        widget = TestDayCalendarWidget()
        assert (
            await widget.get_day_description(self.update, self.context, some_date)
            == TestDayCalendarWidget.day_description
        )

    async def test_get_current_date_uses_current_date_attribute_and_confirm_description(self):
        """Test get_current_date returns the class attribute and confirm description format."""

        class TestWithCustomDate(CalendarWidget):
            current_date = date(2000, 1, 2)

        widget = TestWithCustomDate()
        current = await widget.get_current_date(self.update, self.context)
        assert current == date(2000, 1, 2)

        desc = await widget.get_confirm_description(self.update, self.context, current)
        assert desc == '2 Jan 2000'

    async def test_get_days_returns_month_grid_with_expected_blanks_and_captions(self):
        """Test _get_days returns full month grid with blanks and correct day captions."""
        widget = TestDayCalendarWidget()
        year, month = 2020, 2  # leap year, starts on Saturday
        start = date(year, month, 1)
        days = await widget._get_days(self.update, self.context, start)

        # Blanks equal zeros in monthcalendar, non-nones equal days in month
        weeks = calendar.monthcalendar(year, month)
        blanks = sum(day == 0 for week in weeks for day in week)
        last_day = calendar.monthrange(year, month)[1]

        none_count = sum(1 for day, _ in days if day is None)
        some_days = [int(text) for day, text in days if day is not None]

        assert none_count == blanks
        assert len(some_days) == last_day
        assert some_days[0] == 1
        assert some_days[-1] == last_day

    async def test_get_days_respects_left_and_right_boundaries(self):
        """Test _get_days marks out-of-bound days as blanks according to boundaries."""

        class TestCalendarWidgetWithBoundaries(CalendarWidget):
            left_boundary = date(2020, 2, 5)
            right_boundary = date(2020, 2, 20)

        widget = TestCalendarWidgetWithBoundaries()
        start = date(2020, 2, 1)
        days = await widget._get_days(self.update, self.context, start)

        in_range_days = [day for day, _ in days if day is not None]
        assert in_range_days[0] == date(2020, 2, 5)
        assert in_range_days[-1] == date(2020, 2, 20)
        expect_num_of_available_days = 16
        assert len(in_range_days) == expect_num_of_available_days

    async def test_get_handler_button_builds_button_with_payload_and_handler(self):
        """Test _get_handler_button creates a Button with expected attributes and payload JSON."""

        def handler(_update, _context):
            return DEFAULT_STATE

        payload = {'unit': CalendarUnit.DAY, 'date': ['2025', '10', '07']}
        button = CalendarWidget._get_handler_button(
            'Caption',
            handler,
            payload,
            chat_id=self.chat_id,
        )

        assert isinstance(button, Button)
        assert button.caption == 'Caption'
        assert button.chat_id == self.chat_id
        assert button.source == handler
        assert isinstance(button.payload, str)
        assert '2025' in button.payload

    async def test_get_months_or_years_produces_leading_and_trailing_empty_slots_for_months(self):
        """Test _get_months_or_years returns Nones before/after when outside boundaries (months)."""

        class TestCalendarWidgetWithBoundaries(CalendarWidget):
            left_boundary = date(2020, 2, 1)
            right_boundary = date(2020, 4, 30)

        widget = TestCalendarWidgetWithBoundaries()
        start_date = date(2020, 1, 1)
        number_of_months = 6  # Jan..Jun
        items = await widget._get_months_or_years(
            self.update,
            self.context,
            CalendarUnit.MONTH,
            start_date,
            items_num=number_of_months,
        )

        # Expect: Jan before range -> None, Feb/Mar/Apr valid, May/Jun after range -> None, None
        assert len(items) == number_of_months
        assert items[0] is None
        assert [d.month for d in items[1:4] if d is not None] == [2, 3, 4]
        assert items[4] is None
        assert items[5] is None

    async def test_get_months_or_years_produces_leading_and_trailing_empty_slots_for_years(self):
        """Test _get_months_or_years returns Nones before/after when outside boundaries (years)."""

        class TestCalendarWidgetWithBoundaries(CalendarWidget):
            left_boundary = date(2019, 1, 1)
            right_boundary = date(2021, 12, 31)

        widget = TestCalendarWidgetWithBoundaries()
        start_date = date(2018, 1, 1)
        number_of_years = 6  # 2018..2023
        items = await widget._get_months_or_years(
            self.update,
            self.context,
            CalendarUnit.YEAR,
            start_date,
            items_num=number_of_years,
        )

        # Expect: 2018 before range -> None; 2019, 2020, 2021 valid; 2022, 2023 after -> None, None
        assert len(items) == number_of_years
        assert items[0] is None
        assert [d.year for d in items[1:4] if d is not None] == [2019, 2020, 2021]
        assert items[4] is None
        assert items[5] is None

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
        assert len(arranged_buttons[0]) == row_size
        assert len(arranged_buttons[1]) == row_size

    async def test_getting_calendar_description_that_includes_result_date(self):
        """Test getting the description that includes the result date."""
        actual = await TestDayCalendarWidget().get_confirm_description(
            self.update,
            self.context,
            datetime(1, 1, 1, tzinfo=timezone.utc),
        )
        assert actual == '1 Jan 1'

    def test_getting_date_as_list(self):
        """Test _date_to_list returns [year, month, day] as strings."""
        assert CalendarWidget._date_to_list(date(2025, 10, 7)) == ['2025', '10', '7']

    async def test_getting_left_boundary(self):
        """Test getting the left boundary of the given calendar unit."""
        date = datetime(10, 10, 10, tzinfo=timezone.utc).date()

        actual = _get_left_boundary(date, CalendarUnit.DAY)
        assert actual == date

        actual = _get_left_boundary(date, CalendarUnit.MONTH)
        assert actual == datetime(10, 10, 1, tzinfo=timezone.utc).date()

        actual = _get_left_boundary(date, CalendarUnit.YEAR)
        assert actual == datetime(10, 1, 1, tzinfo=timezone.utc).date()

    async def test_getting_right_boundary(self):
        """Test getting the right boundary of the given calendar unit."""
        date = datetime(10, 10, 10, tzinfo=timezone.utc).date()

        actual = _get_right_boundary(date, CalendarUnit.DAY)
        assert actual == date

        actual = _get_right_boundary(date, CalendarUnit.MONTH)
        assert actual == datetime(10, 10, 31, tzinfo=timezone.utc).date()

        actual = _get_right_boundary(date, CalendarUnit.YEAR)
        assert actual == datetime(10, 12, 31, tzinfo=timezone.utc).date()

    async def test_getting_month_name(self):
        """Test getting the translated month names."""
        expected = [
            'янв',
            'фев',
            'мар',
            'апр',
            'май',
            'июн',
            'июл',
            'авг',
            'сен',
            'окт',
            'ноя',
            'дек',
        ]
        assert [
            TestDayCalendarWidget.get_month_name(month, 'ru') for month in range(1, 13)
        ] == expected

        self.context.user_data.pop('language_code', None)

    @catch_render_config()
    async def test_month_calendar_page_render_after_calling_jump_handler(self, actual):
        """Test getting the month calendar page using the `jump` handler."""
        await TestMonthCalendarWidget().jump(self.update, self.context)

        expected = self.prepare_final_render_config(
            RenderConfig(
                as_new_message=True,
                description=TestMonthCalendarWidget.month_description,
                keyboard=[
                    *await TestMonthCalendarWidget()._build_months(self.update, self.context, None),
                    *await TestMonthCalendarWidget().add_extra_keyboard(self.update, self.context),
                ],
            ),
        )
        assert actual.final_render_config == expected

    @catch_render_config()
    async def test_month_or_year_render_after_calling_on_month_or_year_click(self, actual):
        """Test rendering after clicking month/year navigation button."""
        payload = {'unit': CalendarUnit.YEAR, 'date': ['2024', '10', '01']}
        storage = {'key': json.dumps(payload)}

        with (
            patch(
                'hammett.core.screen.get_callback_query',
                return_value=SimpleNamespace(message=self.message, data='key'),
            ),
            patch('hammett.core.handlers.get_payload_storage', return_value=storage),
        ):
            widget = TestYearCalendarWidget()
            state = await widget._on_month_or_year_click(self.update, self.context)

            current_date = date(*map(int, payload['date']))
            keyboard, unit = await widget._build_keyboard(
                self.update,
                self.context,
                unit=CalendarUnit.MONTH,
                current_date=current_date,
            )
            expected = self.prepare_final_render_config(
                RenderConfig(
                    message_id=self.message_id,
                    description=await widget._get_description(
                        self.update,
                        self.context,
                        unit,
                        current_date,
                    ),
                    keyboard=keyboard,
                ),
            )
            assert actual.final_render_config == expected
            assert state == DEFAULT_STATE

    async def test_set_left_boundary_default(self):
        """Test default left boundary is the earliest possible date."""
        widget = TestDayCalendarWidget()
        boundary = await widget.set_left_boundary(self.update, self.context)
        assert boundary == date(1, 1, 1)

    async def test_set_right_boundary_default(self):
        """Test default right boundary is the farthest possible date."""
        widget = TestDayCalendarWidget()
        boundary = await widget.set_right_boundary(self.update, self.context)
        assert boundary == date(2999, 12, 31)

    @catch_render_config()
    async def test_year_calendar_page_render_after_calling_move_handler(self, actual):
        """Test getting the year calendar page using the `move` handler."""
        await TestYearCalendarWidget().move(self.update, self.context)

        expected = self.prepare_final_render_config(
            RenderConfig(
                description=TestYearCalendarWidget.year_description,
                keyboard=[
                    *await TestYearCalendarWidget()._build_years(self.update, self.context, None),
                    *await TestYearCalendarWidget().add_extra_keyboard(self.update, self.context),
                ],
            ),
        )
        assert actual.final_render_config == expected

    @catch_render_config()
    async def test_navigation_render_after_calling_on_navigation_click(self, actual):
        """Test rendering after clicking back/next navigation buttons."""
        payload = {'unit': CalendarUnit.MONTH, 'date': ['2024', '10', '01']}
        storage = {'key': json.dumps(payload)}

        with (
            patch(
                'hammett.core.screen.get_callback_query',
                return_value=SimpleNamespace(message=self.message, data='key'),
            ),
            patch('hammett.core.handlers.get_payload_storage', return_value=storage),
        ):
            widget = TestMonthCalendarWidget()
            await widget._on_navigation_click(self.update, self.context)

            current_date = date(*map(int, payload['date']))
            keyboard, unit = await widget._build_keyboard(
                self.update,
                self.context,
                unit=payload['unit'],
                current_date=current_date,
            )
            expected = self.prepare_final_render_config(
                RenderConfig(
                    message_id=self.message_id,
                    description=await widget._get_description(
                        self.update,
                        self.context,
                        unit,
                        current_date,
                    ),
                    keyboard=keyboard,
                ),
            )
            assert actual.final_render_config == expected

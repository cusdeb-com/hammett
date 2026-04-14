"""The module contains the implementation of the calendar widget."""

import calendar
import itertools
import json
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta

from hammett.core.button import Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import I18NMixin
from hammett.utils.translation import gettext as _
from hammett.widgets.base import BaseWidget

if TYPE_CHECKING:
    from typing import Any, Self

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.types.core import Handler, Keyboard, State


class CalendarUnit(StrEnum):
    """The class represents all available calendar units."""

    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'


def _arrange_buttons_into_rows(buttons: 'list[Button]', row_size: int) -> 'Keyboard':
    """Arrange the buttons into rows based on the row size.

    Returns:
        Arranged buttons into rows.

    """
    return [
        buttons[i : i + row_size] for i in range(0, max(len(buttons) - row_size, 0) + 1, row_size)
    ]


def _get_left_boundary(date_: 'date', unit: 'CalendarUnit') -> 'date':
    """Return the earliest date in the calendar unit.

    Returns:
        The earliest date in the calendar unit.

    """
    if unit == CalendarUnit.YEAR:
        return date_.replace(month=1, day=1)

    if unit == CalendarUnit.MONTH:
        return date_.replace(day=1)

    return date_  # for CalendarUnit.DAY


def _get_right_boundary(date_: 'date', unit: 'CalendarUnit') -> 'date':
    """Return the latest date in the calendar unit.

    Returns:
        The latest date in the calendar unit.

    """
    if unit == CalendarUnit.YEAR:
        return date_.replace(month=12, day=31)

    if unit == CalendarUnit.MONTH:
        return date_.replace(day=calendar.monthrange(date_.year, date_.month)[1])

    return date_  # for CalendarUnit.DAY


class CalendarWidget(BaseWidget, I18NMixin):
    """The class implements the calendar widget."""

    current_date: 'date | None' = None
    initial_unit: 'CalendarUnit' = CalendarUnit.YEAR
    left_boundary: 'date | None' = None
    right_boundary: 'date | None' = None

    day_description: str = 'Choose the day.'
    month_description: str = 'Choose the month.'
    year_description: str = 'Choose the year.'

    middle_day_caption: str = '{month} {year}'
    middle_month_caption: str = '{year}'
    middle_year_caption: str = ' '

    back_caption: str = '⏮'
    disabled_caption: str = '🔚'
    next_caption: str = '⏭'

    month_row_size: int = 4
    year_row_size: int = 5
    year_column_size: int = 5

    async def _build_days(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        current_date: 'date | None',
        chat_id: int | None = 0,
    ) -> 'Keyboard':
        """Build the day selection keyboard.

        Returns:
            Day selection keyboard.

        """
        current_date = (
            await self.get_current_date(update, context) if current_date is None else current_date
        )
        days_num = calendar.monthrange(current_date.year, current_date.month)[1]
        start_date = current_date.replace(day=1)

        return [
            *[
                [
                    self._get_handler_button(  # days of week buttons
                        _(f'{weekday}', await self.get_language_code(update, context)),  # noqa: INT001
                        self._do_nothing,
                    )
                    for weekday in calendar.day_abbr
                ],
            ],
            *_arrange_buttons_into_rows(  # days buttons
                [
                    self._get_handler_button(
                        caption,
                        self.on_day_click,
                        {
                            'unit': CalendarUnit.DAY,
                            'date': self._date_to_list(date_),
                        },
                        chat_id=chat_id,
                    )
                    if isinstance(date_, date)
                    else self._get_handler_button(caption, self._do_nothing)
                    for date_, caption in await self._get_days(update, context, start_date)
                ],
                row_size=7,
            ),
            *await self._build_navigation_buttons(
                update,
                context,
                CalendarUnit.DAY,
                current_date=current_date,
                chat_id=chat_id,
                unit_size=relativedelta(months=1),
                left_boundary=_get_left_boundary(
                    start_date + relativedelta(days=days_num - 1),
                    CalendarUnit.MONTH,
                ),
                right_boundary=_get_right_boundary(start_date, CalendarUnit.MONTH),
            ),
        ]

    async def _build_months(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        current_date: 'date | None',
        chat_id: int | None = 0,
    ) -> 'Keyboard':
        """Build the month selection keyboard.

        Returns:
            Month selection keyboard.

        """
        current_date = (
            await self.get_current_date(update, context) if current_date is None else current_date
        )
        start_date = current_date.replace(month=1)
        return [
            *_arrange_buttons_into_rows(  # month buttons
                [
                    self._get_handler_button(
                        self.get_month_name(
                            date_.month,
                            await self.get_language_code(update, context),
                        ),
                        self._on_month_or_year_click,
                        {
                            'unit': CalendarUnit.MONTH,
                            'date': self._date_to_list(date_),
                        },
                        chat_id=chat_id,
                    )
                    if isinstance(date_, date)
                    else self._get_handler_button(' ', self._do_nothing)
                    for date_ in await self._get_months_or_years(
                        update,
                        context,
                        CalendarUnit.MONTH,
                        start_date,
                        12,
                    )
                ],
                self.month_row_size,
            ),
            *await self._build_navigation_buttons(
                update,
                context,
                CalendarUnit.MONTH,
                current_date=current_date,
                chat_id=chat_id,
                unit_size=relativedelta(months=12),
                left_boundary=_get_right_boundary(start_date, CalendarUnit.MONTH),
                right_boundary=_get_left_boundary(start_date.replace(month=12), CalendarUnit.MONTH),
            ),
        ]

    async def _build_keyboard(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        unit: 'CalendarUnit | None' = None,
        current_date: 'date | None' = None,
        chat_id: int | None = 0,
    ) -> 'tuple[Keyboard, str]':
        """Return a keyboard based on the calendar unit.

        Returns:
            Keyboard layout corresponding to the specified calendar unit,
            and the unit itself.

        """
        keyboard = []
        unit = unit or await self.get_initial_unit(update, context)
        if unit == CalendarUnit.YEAR:
            keyboard = await self._build_years(update, context, current_date, chat_id)
        elif unit == CalendarUnit.MONTH:
            keyboard = await self._build_months(update, context, current_date, chat_id)
        elif unit == CalendarUnit.DAY:
            keyboard = await self._build_days(update, context, current_date, chat_id)

        return [*keyboard, *(await self.add_extra_keyboard(update, context))], unit

    async def _build_navigation_buttons(  # noqa: PLR0913, PLR0917
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        unit: 'CalendarUnit',
        current_date: 'date',
        unit_size: 'relativedelta',
        left_boundary: 'date',
        right_boundary: 'date',
        chat_id: int | None = 0,
    ) -> 'Keyboard':
        """Build a keyboard with navigation buttons.

        Returns:
            Keyboard with navigation buttons.

        """
        current_date = (
            await self.get_current_date(update, context) if current_date is None else current_date
        )
        year, month, day = self._date_to_list(current_date)

        next_date = right_boundary + relativedelta(**{f'{unit.value}s': 1})  # type: ignore[arg-type]
        prev_date = left_boundary - relativedelta(**{f'{unit.value}s': 1})  # type: ignore[arg-type]

        month = self.get_month_name(int(month), await self.get_language_code(update, context))
        middle_button_caption = getattr(
            self,
            f'middle_{unit.value}_caption',
            '',
        ).format(
            **dict(
                zip(
                    [CalendarUnit.YEAR.value, CalendarUnit.MONTH.value, CalendarUnit.DAY.value],
                    [year, month, day],
                    strict=True,
                ),
            ),
        )

        return [
            [
                # Previous button
                self._get_handler_button(
                    self.back_caption,
                    self._on_navigation_click,
                    {
                        'unit': unit,
                        'date': self._date_to_list(current_date - unit_size),
                    },
                    chat_id=chat_id,
                )
                if prev_date >= await self.set_left_boundary(update, context)  # prev exists
                else self._get_handler_button(self.disabled_caption, self._do_nothing),
                # Middle button
                self._get_handler_button(
                    middle_button_caption,
                    self._do_nothing if unit == CalendarUnit.YEAR else self._on_navigation_click,
                    {
                        'unit': CalendarUnit.MONTH
                        if unit == CalendarUnit.DAY
                        else CalendarUnit.YEAR,
                        'date': self._date_to_list(current_date),
                    },
                    chat_id=chat_id,
                ),
                # Next button
                self._get_handler_button(
                    self.next_caption,
                    self._on_navigation_click,
                    {
                        'unit': unit,
                        'date': self._date_to_list(current_date + unit_size),
                    },
                    chat_id=chat_id,
                )
                if next_date <= await self.set_right_boundary(update, context)  # next exists
                else self._get_handler_button(self.disabled_caption, self._do_nothing),
            ],
        ]

    async def _build_years(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        current_date: 'date | None',
        chat_id: int | None = 0,
    ) -> 'Keyboard':
        """Build the year selection keyboard.

        Returns:
            Year selection keyboard.

        """
        current_date = (
            await self.get_current_date(update, context) if current_date is None else current_date
        )
        years_num = self.year_row_size * self.year_column_size
        start_date = current_date - relativedelta(years=(years_num - 1) // 2)
        return [
            *_arrange_buttons_into_rows(  # year buttons
                [
                    self._get_handler_button(
                        f'{date_.year}',
                        self._on_month_or_year_click,
                        {
                            'unit': CalendarUnit.YEAR,
                            'date': self._date_to_list(date_),
                        },
                        chat_id=chat_id,
                    )
                    if isinstance(date_, date)
                    else self._get_handler_button(' ', self._do_nothing)
                    for date_ in await self._get_months_or_years(
                        update,
                        context,
                        CalendarUnit.YEAR,
                        start_date,
                        years_num,
                    )
                ],
                self.year_row_size,
            ),
            *await self._build_navigation_buttons(
                update,
                context,
                CalendarUnit.YEAR,
                current_date=current_date,
                chat_id=chat_id,
                unit_size=relativedelta(years=years_num),
                left_boundary=_get_right_boundary(start_date, CalendarUnit.YEAR),
                right_boundary=_get_left_boundary(
                    start_date + relativedelta(years=years_num - 1),
                    CalendarUnit.YEAR,
                ),
            ),
        ]

    @staticmethod
    def _date_to_list(date_: 'date') -> list[str]:
        """Return the date as a list.

        Returns:
            Date as a list.

        """
        return list(map(str, date_.timetuple()[:3]))

    @register_button_handler
    async def _do_nothing(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoke by a disabled button.

        Returns:
            State after clicking on a disabled button.

        """
        return DEFAULT_STATE

    async def _get_days(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        start_date: 'date',
    ) -> 'list[tuple[date | None, str]]':
        """Return a list of dates starting from the given date.

        Returns:
            List of dates with their captions, starting from the specified date.

        """
        year = start_date.year
        month = start_date.month

        left_boundary = await self.set_left_boundary(update, context)
        right_boundary = await self.set_right_boundary(update, context)

        return await self.get_dates_with_captions(
            update,
            context,
            year,
            month,
            [
                date(year, month, day)
                if day != 0 and left_boundary <= date(year, month, day) <= right_boundary
                else None
                for day in itertools.chain(*calendar.monthcalendar(year, month))
            ],
        )

    async def _get_description(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        unit: 'CalendarUnit | str',
        date_: 'date',
    ) -> str:
        """Return a description based on the calendar unit.

        Returns:
            Description for the calendar widget, based on the specified unit.

        """
        return (
            await self.get_year_description(update, context, date_)
            if unit == CalendarUnit.YEAR
            else await self.get_month_description(update, context, date_)
            if unit == CalendarUnit.MONTH
            else await self.get_day_description(update, context, date_)
        )

    @staticmethod
    def _get_handler_button(
        caption: str,
        source: 'Handler',
        payload: dict[str, str | list[str]] | None = None,
        chat_id: int | None = 0,
    ) -> 'Button':
        """Return a button built from the provided data.

        Returns:
            Button.

        """
        return Button(
            caption,
            source,
            source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            chat_id=chat_id,
            payload=payload if payload is None else json.dumps(payload),
        )

    async def _get_months_or_years(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        unit: 'CalendarUnit',
        start_date: 'date',
        items_num: int,
    ) -> 'list[date | None]':
        """Return the list of dates from the starting date.

        Returns:
            List of dates from the starting date.

        """
        dates = []
        empty_before = 0
        empty_after = 0

        left_boundary = await self.set_left_boundary(update, context)
        right_boundary = await self.set_right_boundary(update, context)

        for i in range(items_num):
            date_ = start_date + relativedelta(**{f'{unit.value}s': i})  # type: ignore[arg-type]
            if left_boundary > _get_right_boundary(date_, unit):
                empty_before += 1
            elif right_boundary < _get_left_boundary(date_, unit):
                empty_after += 1
            else:
                dates.append(date_)

        return [None] * empty_before + dates + [None] * empty_after

    async def _init(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        config: 'RenderConfig | None' = None,
        **kwargs: 'Any',
    ) -> 'State':
        """Initialize the widget.

        Returns:
            State after widget initialization.

        """
        current_date = kwargs.get('current_date') or await self.get_current_date(update, context)

        config = config or RenderConfig()
        keyboard, unit = await self._build_keyboard(
            update,
            context,
            current_date=current_date,
            chat_id=config.chat_id,
        )
        config.description = await self._get_description(update, context, unit, current_date)
        config.keyboard = keyboard

        await self.render(update, context, config=config, **kwargs)
        return DEFAULT_STATE

    @register_button_handler
    async def _on_month_or_year_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoke when a month or year button is clicked.

        Returns:
            State after clicking a month or year button.

        """
        payload = json.loads(await self.get_payload(update, context))
        unit = payload['unit']
        current_date = date(*map(int, payload['date']))

        keyboard, unit = await self._build_keyboard(
            update,
            context,
            unit=CalendarUnit.MONTH if unit == CalendarUnit.YEAR else CalendarUnit.DAY,
            current_date=current_date,
        )
        await self.render(
            update,
            context,
            config=RenderConfig(
                description=await self._get_description(update, context, unit, current_date),
                keyboard=keyboard,
            ),
        )
        return DEFAULT_STATE

    @register_button_handler
    async def _on_navigation_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Invoke when a navigation button is clicked.

        Returns:
            State after clicking a navigation button.

        """
        payload = json.loads(await self.get_payload(update, context))
        current_date = date(*map(int, payload['date']))

        keyboard, unit = await self._build_keyboard(
            update,
            context,
            unit=payload['unit'],
            current_date=current_date,
        )
        await self.render(
            update,
            context,
            config=RenderConfig(
                description=await self._get_description(update, context, unit, current_date),
                keyboard=keyboard,
            ),
        )
        return DEFAULT_STATE

    #
    # Public methods
    #

    async def get_confirm_description(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
        result_date: 'date',
    ) -> str:
        """Return the widget description for the selected date.

        Returns:
            Description of the widget with the selected date.

        """
        language_code = await self.get_language_code(update, context)
        return (
            f'{result_date.day} '
            f'{self.get_month_name(result_date.month, language_code)} '
            f'{result_date.year}'
        )

    async def get_current_date(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'date':
        """Return the `current_date` attribute of the widget.

        Returns:
            `current_date` attribute of the widget.

        """
        return self.current_date or datetime.now(tz=UTC).date()

    async def get_dates_with_captions(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _year: int,
        _month: int,
        dates: 'list[date | None]',
    ) -> 'list[tuple[date | None, str]]':
        """Return the list of dates with their captions.

        Returns:
            List of dates with their captions.

        """
        return [(None, ' ') if date_ is None else (date_, str(date_.day)) for date_ in dates]

    async def get_day_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _current_date: 'date',
    ) -> str:
        """Return the `day_description` attribute of the widget.

        Returns:
            `day_description` attribute of the widget.

        """
        return self.day_description

    async def get_initial_unit(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'CalendarUnit':
        """Return the `initial_unit` attribute of the widget.

        Returns:
            `initial_unit` attribute of the widget.

        """
        return self.initial_unit

    async def get_month_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _current_date: 'date',
    ) -> str:
        """Return the `month_description` attribute of the widget.

        Returns:
            `month_description` attribute of the widget.

        """
        return self.month_description

    @staticmethod
    def get_month_name(month: int, language_code: str) -> str:
        """Return the translated abbreviation of the specified month.

        Returns:
            Translated  abbreviation of the month.

        """
        return _(calendar.month_abbr[month], language_code)

    async def get_year_description(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
        _current_date: 'date',
    ) -> str:
        """Return the `year_description` attribute of the widget.

        Returns:
            `year_description` attribute of the widget.

        """
        return self.year_description

    async def set_right_boundary(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'date':
        """Return the latest date that can be selected in the calendar.

        Returns:
            The latest date that can be selected in the calendar.

        """
        return self.right_boundary or date(2999, 12, 31)

    async def set_left_boundary(
        self: 'Self',
        _update: 'Update | None',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'date':
        """Return the earliest date that can be selected in the calendar.

        Returns:
            The earliest date that can be selected in the calendar.

        """
        return self.left_boundary or date(1, 1, 1)

    async def jump(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is sent as a new message.

        Returns:
            State after jumping to the widget.

        """
        return await self._init(update, context, config=RenderConfig(as_new_message=True), **kwargs)

    async def move(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        **kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget re-renders the previous message.

        Returns:
            State after moving to the widget.

        """
        return await self._init(update, context, **kwargs)

    @register_button_handler
    async def on_day_click(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'State':
        """Handle widget behavior after a day has been selected, i.e. when
        date selection is fully complete.

        Returns:
            State after selecting the day.

        """
        payload = json.loads(await self.get_payload(update, context))
        current_date = date(*map(int, payload['date']))

        await self.render(
            update,
            context,
            config=RenderConfig(
                description=await self.get_confirm_description(update, context, current_date),
                keyboard=await self.add_extra_keyboard(update, context),
            ),
        )
        return DEFAULT_STATE

    async def send(
        self: 'Self',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
        **kwargs: 'Any',
    ) -> 'State':
        """Handle the case when the widget is used as a notification.

        Returns:
            State after sending the widget.

        """
        config = config or RenderConfig()
        config.as_new_message = True

        return await self._init(None, context, config=config, **kwargs)

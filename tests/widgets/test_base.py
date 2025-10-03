"""Tests for base widget classes in hammett.widgets.base."""

# ruff: noqa: SLF001

from types import SimpleNamespace
from unittest.mock import patch

from hammett.core.constants import FinalRenderConfig
from hammett.core.exceptions import FailedToGetDataAttributeOfQuery, PayloadIsEmpty
from hammett.test.base import BaseTestCase
from hammett.widgets.base import BaseChoiceWidget, BaseStateWidget
from hammett.widgets.exceptions import (
    ChoiceEmojisAreUndefined,
    ChoicesFormatIsInvalid,
    FailedToGetStateKey,
    NoChoicesSpecified,
)
from tests.base import BaseTestScreenWithDescription


class BaseChoiceWidgetWithChoices(BaseChoiceWidget):
    """The class implements a concrete subclass for testing BaseChoiceWidget behavior."""

    choices = (
        ('a', 'Option A'),
        ('b', 'Option B'),
    )


class BaseChoiceWidgetWithEmojis(BaseChoiceWidget):
    """The class implements a concrete subclass for testing BaseChoiceWidget behavior."""

    chosen_emoji = '✅'
    unchosen_emoji = '⭕'


class TestBaseChoiceWidget(
    BaseChoiceWidgetWithEmojis,
    BaseChoiceWidgetWithChoices,
    BaseTestScreenWithDescription,
    BaseChoiceWidget,
):
    """The class implements a subclass for testing BaseChoiceWidget with choices and emojis."""

    async def _initialize_choices(self, _update, _context, choices, **_kwargs):
        """Initialize choices."""
        return tuple((False, code, name) for code, name in choices)


class TestStateWidget(BaseStateWidget):
    """The class implements a concrete subclass for testing BaseStateWidget behavior."""


class BaseStateWidgetTests(BaseTestCase):
    """The class implements tests for BaseStateWidget internals."""

    async def test_get_state_key_raises_when_message_is_missing(self):
        """Test _get_state_key raises FailedToGetStateKey when callback query has no message."""
        widget = TestStateWidget()
        with (
            patch('hammett.widgets.base.get_callback_query', return_value=SimpleNamespace()),
            self.assertRaises(FailedToGetStateKey),
        ):
            await widget._get_state_key(self.update)

    async def test_get_state_key_returns_correct_key(self):
        """Test _get_state_key returns the correct state key."""
        widget = TestStateWidget()
        state_key = await widget._get_state_key(
            chat_id=self.chat.id,
            message_id=self.message.message_id,
        )
        self.assertEqual(
            f'{widget.__class__.__name__}_{self.chat.id}_{self.message.message_id}',
            state_key,
        )

    async def test_get_state_value_returns_none_when_failed_to_get_state_key(self):
        """Test get_state_value returns None if _get_state_key raises FailedToGetStateKey."""
        self.context.user_data.update({1: 1})

        widget = TestStateWidget()
        with patch(
            'hammett.widgets.base.BaseStateWidget._get_state_key',
            side_effect=FailedToGetStateKey,
        ):
            actual = await widget.get_state_value(self.update, self.context, 'choices')
            self.assertIsNone(actual)

    async def test_initialized_state_not_implemented_raises(self):
        """Test that _initialized_state raises NotImplementedError by default."""
        widget = TestStateWidget()
        with self.assertRaises(NotImplementedError):
            await widget._initialized_state(
                self.update,
                self.context,
                self.message,
                FinalRenderConfig(),
            )

    async def test_set_and_get_state_value_roundtrip(self):
        """Test that set_state_value stores the value and get_state_value retrieves it."""
        self.context.user_data.update({1: 1})

        widget = TestStateWidget()
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            await widget.set_state_value(self.update, self.context, 'foo', 'bar')
            actual = await widget.get_state_value(self.update, self.context, 'foo')
            self.assertEqual(actual, 'bar')

    async def test_set_return_none_when_user_data_is_empty(self):
        """Test that set_state_value returns None when user_data is empty."""
        widget = TestStateWidget()
        actual = await widget.set_state_value(self.update, self.context, 'foo', 'bar')
        self.assertIsNone(actual)


class BaseChoiceWidgetTests(BaseTestCase):
    """The class implements the tests for BaseChoiceWidget."""

    async def test_build_keyboard_raises_invalid_choice_format(self):
        """Test that build_keyboard raises an error if the choices are in an invalid format."""
        widget = TestBaseChoiceWidget()
        bad_initialized_choices = (('a', 'Option A'),)
        with self.assertRaises(ChoicesFormatIsInvalid):
            await widget._build_keyboard(self.update, self.context, bad_initialized_choices)

    async def test_build_keyboard_raises_no_choices_specified(self):
        """Test that build_keyboard raises an error if no choices are specified."""
        widget = TestBaseChoiceWidget()
        with self.assertRaises(NoChoicesSpecified):
            await widget._build_keyboard(self.update, self.context, ())

    async def test_build_keyboard_with_valid_initialized_choices(self):
        """Test that build_keyboard returns a keyboard with the correct captions."""
        widget = TestBaseChoiceWidget()
        initialized_choices = (
            (False, 'a', 'Option A'),
            (True, 'b', 'Option B'),
        )
        keyboard = await widget._build_keyboard(self.update, self.context, initialized_choices)
        captions = [row[0].caption for row in keyboard]
        self.assertEqual(captions, [
            f'{widget.unchosen_emoji} Option A',
            f'{widget.chosen_emoji} Option B',
        ])

    async def test_get_choices_returns_attribute(self):
        """Test that get_choices returns the choices attribute."""
        widget = TestBaseChoiceWidget()
        actual = await widget.get_choices(None, self.context)
        self.assertEqual(actual, widget.choices)

    async def test_get_chosen_choices_filters_true_flags(self):
        """Test that get_chosen_choices filters true flags."""
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestBaseChoiceWidget()
            # Ensure user_data is truthy so set_state_value doesn't early-return
            self.context.user_data.update({'seed': True})
            initialized_choices = (
                (True, 'a', 'Option A'),
                (False, 'b', 'Option B'),
            )
            await widget.set_state_value(self.update, self.context, 'choices', initialized_choices)
            chosen = await widget.get_chosen_choices(self.update, self.context)
            self.assertEqual(chosen, ((True, 'a', 'Option A'),))

    async def test_get_initialized_choices_returns_empty_when_state_unavailable(self):
        """Test that get_initialized_choices returns empty tuple when
        state key can't be resolved.
        """
        widget = TestBaseChoiceWidget()
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(),
        ):
            actual = await widget.get_initialized_choices(self.update, self.context)
            self.assertEqual(actual, ())

    async def test_get_initialized_choices_returns_saved_state(self):
        """Test that get_initialized_choices returns the choices saved in state."""
        widget = TestBaseChoiceWidget()
        # Ensure user_data is truthy and seed state via set_state_value
        self.context.user_data.update({'seed': True})
        choices = (
            (False, 'a', 'Option A'),
            (True, 'b', 'Option B'),
        )
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            await widget.set_state_value(self.update, self.context, 'choices', choices)
            actual = await widget.get_initialized_choices(self.update, self.context)
            self.assertEqual(actual, choices)

    async def test_get_payload_raises_when_payload_not_found(self):
        """Test getting payload fails when payload is absent in storage."""
        with (
            patch(
                'hammett.widgets.base.get_callback_query',
                return_value=SimpleNamespace(data='key'),
            ),
            patch('hammett.core.handlers.get_payload_storage', return_value={}),
            self.assertRaises(PayloadIsEmpty),
        ):
            await TestBaseChoiceWidget.get_payload(self.update, self.context)

    async def test_get_payload_raises_when_query_has_no_data(self):
        """Test getting payload fails when callback query has no data attribute."""
        with (
            patch(
                'hammett.widgets.base.get_callback_query',
                return_value=SimpleNamespace(data=None),
            ),
            self.assertRaises(FailedToGetDataAttributeOfQuery),
        ):
            await TestBaseChoiceWidget.get_payload(self.update, self.context)

    async def test_get_payload_returns_value(self):
        """Test getting payload returns value when payload is present in storage."""
        storage = {'key': 'value'}
        with (
            patch(
                'hammett.widgets.base.get_callback_query',
                return_value=SimpleNamespace(data='key'),
            ),
            patch('hammett.widgets.base.get_payload_storage', return_value=storage),
        ):
            value = await TestBaseChoiceWidget.get_payload(self.update, self.context)
            self.assertEqual(value, 'value')
            self.assertIn('key', storage)

    async def test_initialized_state_returns_empty_choices(self):
        """Test that initialized_state returns the choices."""
        widget = TestBaseChoiceWidget()
        actual = await widget._initialized_state(
            self.update,
            self.context,
            self.message,
            FinalRenderConfig(),
        )
        self.assertEqual(actual, {'choices': ()})

    async def test_initialized_state_returns_passed_choices(self):
        """Test that initialized_state returns the passed choices."""
        widget = TestBaseChoiceWidget()
        actual = await widget._initialized_state(
            self.update,
            self.context,
            self.message,
            FinalRenderConfig(),
            widget.choices,
        )
        self.assertEqual(actual, {'choices': widget.choices})

    async def test_raises_error_if_emojis_are_undefined(self):
        """Test that BaseChoiceWidget raises an error if no emojis are specified."""

        class TestBaseChoiceWidgetWithoutEmojis(BaseChoiceWidgetWithChoices):
            """The class implements a concrete subclass for testing BaseChoiceWidget behavior."""

        with self.assertRaises(ChoiceEmojisAreUndefined):
            TestBaseChoiceWidgetWithoutEmojis()

    async def test_raises_error_if_initialize_choices_is_not_implemented(self):
        """Test that BaseChoiceWidget raises an error if _initialize_choices is not implemented."""

        class TestBaseChoiceWidgetWithoutInitializeChoices(BaseChoiceWidgetWithEmojis):
            """The class implements a concrete subclass for testing BaseChoiceWidget behavior."""

        with self.assertRaises(NotImplementedError):
            await TestBaseChoiceWidgetWithoutInitializeChoices().move(self.update, self.context)

    async def test_raises_error_if_switch_is_not_implemented(self):
        """Test that BaseChoiceWidget raises an error if switch is not implemented."""
        with self.assertRaises(NotImplementedError):
            await TestBaseChoiceWidget().switch(self.update, self.context, ('a', 'Option A'))

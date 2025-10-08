"""The module contains the tests for MultiChoiceWidget."""

# ruff: noqa: SLF001

import json
from types import SimpleNamespace
from unittest.mock import patch

from hammett.core.constants import RenderConfig
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from hammett.widgets.multi_choice_widget import MultiChoiceWidget
from tests.base import BaseTestScreenWithDescription, BaseTestScreenWithMockedRenderer


class BaseTestMultiChoiceWidget(
    MultiChoiceWidget,
    BaseTestScreenWithMockedRenderer,
    BaseTestScreenWithDescription,
):
    """The class implements a base MultiChoiceWidget for testing purposes."""

    choices = (
        ('a', 'Option A'),
        ('b', 'Option B'),
        ('c', 'Option C'),
    )


class TestMultiChoiceWidget(BaseTestMultiChoiceWidget):
    """MultiChoiceWidget without predefined initial value for tests."""


class TestMultiChoiceWidgetWithInitials(BaseTestMultiChoiceWidget):
    """MultiChoiceWidget with predefined initial value for tests."""

    initial_values = ['a', 'b']


class MultiChoiceWidgetTests(BaseTestCase):
    """The class implements the tests for MultiChoiceWidget."""

    async def test_build_keyboard_captions_reflect_selection(self):
        """Test that keyboard captions reflect the chosen/unchosen emojis."""
        widget = TestMultiChoiceWidgetWithInitials()
        initialized = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )

        keyboard = await widget._build_keyboard(self.update, self.context, initialized)
        captions = [row[0].caption for row in keyboard]
        self.assertEqual(captions, [
            f'{widget.chosen_emoji} Option A',
            f'{widget.chosen_emoji} Option B',
            f'{widget.unchosen_emoji} Option C',
        ])

    async def test_initialize_choices_default_marks(self):
        """Test that _initialize_choices marks no choice as selected by default."""
        widget = TestMultiChoiceWidget()
        initialized = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )

        self.assertEqual(
            initialized, (
                (False, 'a', 'Option A'),
                (False, 'b', 'Option B'),
                (False, 'c', 'Option C'),
            ),
        )

    async def test_initialize_choices_marks_with_initial_value(self):
        """Test that _initialize_choices marks only the initial value as chosen."""
        widget = TestMultiChoiceWidgetWithInitials()
        initialized = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )

        self.assertEqual(
            initialized, (
                (True, 'a', 'Option A'),
                (True, 'b', 'Option B'),
                (False, 'c', 'Option C'),
            ),
        )

    @catch_render_config()
    async def test_multi_choice_widget_render_after_calling_jump_handler(self, actual):
        """Test calling the jump handler to get the final render config."""
        widget = TestMultiChoiceWidget()
        await widget.jump(self.update, self.context)

        initialized_choices = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )
        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description='Test description',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                initialized_choices,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_multi_choice_widget_render_after_calling_move_handler(self, actual):
        """Test calling the move handler to get the final render config."""
        widget = TestMultiChoiceWidget()
        await widget.move(self.update, self.context)

        initialized_choices = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )
        expected = self.prepare_final_render_config(RenderConfig(
            description='Test description',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                initialized_choices,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_multi_choice_widget_render_after_calling_send_handler(self, actual):
        """Test calling the send handler to get the final render config."""
        widget = TestMultiChoiceWidget()
        await widget.send(self.context, choices=widget.choices)

        initialized_choices = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )
        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description='Test description',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                initialized_choices,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    async def test_switch_marks_only_selected_choice(self):
        """Test that switch selects a single choice and unselects others."""
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestMultiChoiceWidget()
            await widget.move(self.update, self.context)  # initialize state

            switched = await widget.switch(self.update, self.context, ('b', 'Option B'))
            self.assertEqual(
                switched,
                (
                    (False, 'a', 'Option A'),
                    (True, 'b', 'Option B'),
                    (False, 'c', 'Option C'),
                ),
            )


class BaseChoiceWidgetTestsUsingMultiChoiceWidget(BaseTestCase):
    """The class implements the tests for BaseChoiceWidget using MultiChoiceWidget."""

    @catch_render_config()
    async def test_multi_choice_widget_render_after_calling_on_choice_click_handler(self, actual):
        """Test calling the _on_choice_click handler to get the final render config."""
        callback_query = SimpleNamespace(data='key', message=self.message)
        payload_storage = [
            {'key': json.dumps({'code': 'a', 'name': 'Option A'})},
            {'key': json.dumps({'code': 'b', 'name': 'Option B'})},
        ]
        with (
            patch('hammett.widgets.base.get_callback_query', return_value=callback_query),
            patch('hammett.widgets.base.get_payload_storage', side_effect=payload_storage),
        ):
            widget = TestMultiChoiceWidget()
            await widget.move(self.update, self.context)  # initialize state
            await widget._on_choice_click(self.update, self.context)  # choose Option A

            choices = (
                (True, 'a', 'Option A'),
                (False, 'b', 'Option B'),
                (False, 'c', 'Option C'),
            )
            expected = self.prepare_final_render_config(RenderConfig(
                description=widget.description,
                keyboard=await widget._build_keyboard(
                    self.update,
                    self.context,
                    choices,
                ),
            ))
            self.assertEqual(actual.final_render_config, expected)

            await widget._on_choice_click(self.update, self.context)  # choose Option B

            choices = (
                (True, 'a', 'Option A'),
                (True, 'b', 'Option B'),
                (False, 'c', 'Option C'),
            )
            expected = self.prepare_final_render_config(RenderConfig(
                description=widget.description,
                keyboard=await widget._build_keyboard(
                    self.update,
                    self.context,
                    choices,
                ),
            ))
            self.assertEqual(actual.final_render_config, expected)

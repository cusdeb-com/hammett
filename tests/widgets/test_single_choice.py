"""The module contains the tests for SingleChoiceWidget."""

# ruff: noqa: SLF001

from types import SimpleNamespace
from unittest.mock import patch

from hammett.core.constants import RenderConfig
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from hammett.widgets.single_choice_widget import SingleChoiceWidget
from tests.base import BaseTestScreenWithDescription, BaseTestScreenWithMockedRenderer


class BaseTestSingleChoiceWidget(
    SingleChoiceWidget,
    BaseTestScreenWithMockedRenderer,
    BaseTestScreenWithDescription,
):
    """The class implements a base SingleChoiceWidget for testing purposes."""

    choices = (
        ('a', 'Option A'),
        ('b', 'Option B'),
        ('c', 'Option C'),
    )


class TestSingleChoiceWidget(BaseTestSingleChoiceWidget):
    """SingleChoiceWidget without predefined initial value for tests."""


class TestSingleChoiceWidgetWithInitial(BaseTestSingleChoiceWidget):
    """SingleChoiceWidget with predefined initial value for tests."""

    initial_value = 'b'


class SingleChoiceWidgetTests(BaseTestCase):
    """The class implements the tests for SingleChoiceWidget."""

    async def test_build_keyboard_captions_reflect_selection(self):
        """Test that keyboard captions reflect the chosen/unchosen emojis."""
        widget = TestSingleChoiceWidgetWithInitial()
        initialized = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )

        keyboard = await widget._build_keyboard(self.update, self.context, initialized)
        captions = [row[0].caption for row in keyboard]
        self.assertEqual(captions, [
            f'{widget.unchosen_emoji} Option A',
            f'{widget.chosen_emoji} Option B',
            f'{widget.unchosen_emoji} Option C',
        ])

    async def test_initialize_choices_default_marks(self):
        """Test that _initialize_choices marks no choice as selected by default."""
        widget = TestSingleChoiceWidget()
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
        widget = TestSingleChoiceWidgetWithInitial()
        initialized = await widget._initialize_choices(
            self.update,
            self.context,
            widget.choices,
        )

        self.assertEqual(
            initialized, (
                (False, 'a', 'Option A'),
                (True, 'b', 'Option B'),
                (False, 'c', 'Option C'),
            ),
        )

    async def test_switch_marks_only_selected_choice(self):
        """Test that switch selects a single choice and unselects others."""
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestSingleChoiceWidget()
            await widget.move(self.update, self.context)  # initialize state

            switched = await widget.switch(self.update, self.context, ('b', 'Option B'))
            self.assertEqual(
                switched, (
                    (False, 'a', 'Option A'),
                    (True, 'b', 'Option B'),
                    (False, 'c', 'Option C'),
                ),
            )

    @catch_render_config()
    async def test_single_choice_widget_render_after_calling_jump_handler(self, actual):
        """Test calling the jump handler to get the final render config."""
        widget = TestSingleChoiceWidget()
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
    async def test_single_choice_widget_render_after_calling_move_handler(self, actual):
        """Test calling the move handler to get the final render config."""
        widget = TestSingleChoiceWidget()
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
    async def test_single_choice_widget_render_after_calling_send_handler(self, actual):
        """Test calling the send handler to get the final render config."""
        widget = TestSingleChoiceWidget()
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

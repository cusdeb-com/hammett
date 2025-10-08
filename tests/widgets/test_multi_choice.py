"""The module contains the tests for MultiChoiceWidget."""

# ruff: noqa: SLF001

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.constants import RenderConfig
from hammett.core.exceptions import MissingPersistence
from hammett.core.persistence import RedisPersistence
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


class BaseStateWidgetTestsUsingMultiChoiceWidget(BaseTestCase):
    """The class implements extra tests for BaseStateWidget using MultiChoiceWidget."""

    async def test_saving_state_to_user_data_when_widget_is_sent_via_move_handler(self):
        """Test saving the state to user_data when widget is sent via move handler."""
        widget = TestMultiChoiceWidget()
        await widget.move(self.update, self.context)  # initialize state

        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            state_key = await widget._get_state_key(self.update)
            initialized_choices = await widget._initialize_choices(
                self.update,
                self.context,
                widget.choices,
            )

            self.assertIn(initialized_choices, self.context.user_data[state_key].values())


class BaseStateWidgetTestsUsingMultiChoiceWidgetWithoutUpdate(BaseTestCase):
    """The class implements extra tests for BaseStateWidget using MultiChoiceWidget
    without update.
    """

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    async def test_widget_raises_error_when_no_persistence_is_configured(self):
        """Test raising MissingPersistence when no persistence is configured."""
        widget = TestMultiChoiceWidget()
        with self.assertRaises(MissingPersistence):
            await widget.jump(self.update, self.context)

    async def test_post_render_uses_last_message_from_tuple(self):
        """Test that _post_render picks the last message when renderer returns a tuple."""
        mock_persistence = AsyncMock()
        self.context._application.persistence = mock_persistence

        widget = TestMultiChoiceWidget()
        first = SimpleNamespace(message_id=111, chat_id=111)
        last = self.message
        with patch.object(widget.renderer, 'render', new=AsyncMock(return_value=(first, last))):
            await widget.send(self.context)
            mock_persistence.update_user_data.assert_called_once_with(
                last.id,
                self.context._application.user_data[self.user.id],
            )

    @catch_render_config()
    async def test_saving_state_to_persistence_when_persistence_is_configured(self, actual):
        """Test saving the state to persistence when persistence is configured."""
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()

        widget = TestMultiChoiceWidget()
        await widget.send(self.context, choices=widget.choices)

        choices = (
            (False, 'a', 'Option A'),
            (False, 'b', 'Option B'),
            (False, 'c', 'Option C'),
        )
        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=widget.description,
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                choices,
            ),
        ))

        state_key = await widget._get_state_key(
            chat_id=self.chat.id,
            message_id=self.message.message_id,
        )
        user_data = self.context._application.user_data[self.user.id]
        self.assertIn(choices, user_data[state_key].values())
        self.assertEqual(actual.final_render_config, expected)

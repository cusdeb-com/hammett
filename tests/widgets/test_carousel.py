"""The module contains tests for the CarouselWidget."""

# ruff: noqa: SLF001

from types import SimpleNamespace
from unittest.mock import patch

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.constants import RenderConfig
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.persistence import RedisPersistence
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from hammett.widgets.carousel_widget import CarouselWidget
from tests.base import (
    CHAT_ID,
    MESSAGE_ID,
    USER_ID,
    BaseTestScreenWithMockedRenderer,
)

_DATA = {'key1': 'value1', 'key2': 'value2'}


class BaseTestCarouselWidget(CarouselWidget, BaseTestScreenWithMockedRenderer):
    """The class implements the base CarouselWidget for the testing purposes."""

    images = [
        ['cover_1', 'description_1'],
        ['cover_2', 'description_2'],
    ]


class TestCarouselWidget(BaseTestCarouselWidget):
    """The class implements a screen based on CarouselWidget for the testing purposes."""


class TestInfinityCarouselWidget(BaseTestCarouselWidget):
    """The class implements a screen based on CarouselWidget with infinity
    keyboard for the testing purposes.
    """

    infinity = True


class CarouselWidgetTests(BaseTestCase):
    """The class implements the tests for CarouselWidget."""

    def setUp(self):
        """Initialize a persistence object and replace its Redis instance
        with a fake one.
        """
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()

        self.context.user_data.clear()

    async def test_carousel_widget_build_keyboard_disables_back_on_index_error(self):
        """Test disabling the back button when IndexError occurs in _build_keyboard."""
        widget = TestCarouselWidget()
        keyboard = await widget._build_keyboard(
            self.update,
            self.context,
            images=[],
            current_image=1,
        )

        assert keyboard[0][0] == widget._disabled_button
        assert keyboard[0][1] == widget._disabled_button

    @catch_render_config()
    async def test_carousel_widget_infinity_mode_with_back_handler(self, actual):
        """Test calling the next handler to get the final render config in infinity mode."""
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestInfinityCarouselWidget()
            await widget.move(self.update, self.context)  # initialize state

            await widget._back(self.update, self.context)  # back
            expected_next = self.prepare_final_render_config(RenderConfig(
                description='description_2',
                cover='cover_2',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_next, actual.final_render_config)

            await widget._back(self.update, self.context)  # back again
            expected_wrap = self.prepare_final_render_config(RenderConfig(
                description='description_1',
                cover='cover_1',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_wrap, actual.final_render_config)

            await widget._back(self.update, self.context)  # back again
            expected_next = self.prepare_final_render_config(RenderConfig(
                description='description_2',
                cover='cover_2',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_next, actual.final_render_config)

    @catch_render_config()
    async def test_carousel_widget_infinity_mode_with_next_handler(self, actual):
        """Test calling the next handler to get the final render config in infinity mode."""
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestInfinityCarouselWidget()
            await widget.move(self.update, self.context)  # initialize state

            await widget._next(self.update, self.context)  # next
            expected_next = self.prepare_final_render_config(RenderConfig(
                description='description_2',
                cover='cover_2',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_next, actual.final_render_config)

            await widget._next(self.update, self.context)  # next again
            expected_wrap = self.prepare_final_render_config(RenderConfig(
                description='description_1',
                cover='cover_1',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_wrap, actual.final_render_config)

            await widget._next(self.update, self.context)  # next again
            expected_next = self.prepare_final_render_config(RenderConfig(
                description='description_2',
                cover='cover_2',
                keyboard=widget._infinity_keyboard + await widget.add_extra_keyboard(
                    self.update, self.context,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_next, actual.final_render_config)

    @catch_render_config()
    async def test_carousel_widget_render_after_calling_jump_handler(self, actual):
        """Test calling the jump handler to get the final render config."""
        widget = TestCarouselWidget()
        await widget.jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description='description_1',
            cover='cover_1',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                widget.images,
                current_image=0,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_carousel_widget_render_after_calling_move_handler(self, actual):
        """Test calling the move handler to get the final render config."""
        widget = TestCarouselWidget()
        await widget.move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description='description_1',
            cover='cover_1',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                widget.images,
                current_image=0,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_carousel_widget_render_after_calling_next_and_back_handlers(self, actual):
        """Test calling the next and back handlers to get the final render config."""
        widget = TestCarouselWidget()
        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            await widget.move(self.update, self.context)  # initialize state

            await widget._next(self.update, self.context)  # next
            expected_next = self.prepare_final_render_config(RenderConfig(
                description='description_2',
                cover='cover_2',
                keyboard=await widget._build_keyboard(
                    self.update,
                    self.context,
                    widget.images,
                    current_image=1,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_next, actual.final_render_config)

            await widget._back(self.update, self.context)  # back
            expected_back = self.prepare_final_render_config(RenderConfig(
                description='description_1',
                cover='cover_1',
                keyboard=await widget._build_keyboard(
                    self.update,
                    self.context,
                    widget.images,
                    current_image=0,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected_back, actual.final_render_config)

    @catch_render_config()
    async def test_carousel_widget_render_after_calling_send_handler(self, actual):
        """Test calling the send handler to get the final render config."""
        custom_images = [['cover_1', 'description_1']]
        widget = TestCarouselWidget()
        await widget.send(self.context, images=custom_images)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description='description_1',
            cover='cover_1',
            keyboard=await widget._build_keyboard(
                self.update,
                self.context,
                custom_images,
                current_image=0,
            ),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    def test_improperly_configured_images_type(self):
        """Test that non-list images raise ImproperlyConfigured in __init__."""
        class BadImagesWidget(CarouselWidget):
            images = 'not-a-list'

        with self.assertRaises(ImproperlyConfigured):
            BadImagesWidget()

    def test_improperly_configured_missing_captions(self):
        """Test that missing captions raise ImproperlyConfigured in __init__."""
        class BadCaptionsWidget(CarouselWidget):
            back_caption = next_caption = disable_caption = ''

        with self.assertRaises(ImproperlyConfigured):
            BadCaptionsWidget()


class CarouselWidgetWithoutUpdateTests(BaseTestCase):
    """The class implements the tests for CarouselWidget without update."""

    def setUp(self):
        """Initialize a persistence object and replace its Redis instance
        with a fake one.
        """
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    async def test_updating_user_data_after_sending_carousel_widget_as_notification(self):
        """Test updating the user_data when a screen based on CarouselWidget is sent
        as a notification.
        """
        self.context._application.user_data = {USER_ID: _DATA}

        widget = TestCarouselWidget()
        await widget.send(self.context)

        updated_user_data = self.context._application.persistence.user_data
        state_key = await widget._get_state_key(
            chat_id=CHAT_ID,
            message_id=MESSAGE_ID,
        )
        assert updated_user_data == {USER_ID: {state_key: {'images': widget.images}, **_DATA}}

    @catch_render_config()
    async def test_carousel_render_after_calling_move_handler_without_update(self, actual):
        """Test calling the move handler to get the final render config without update."""
        caption = 'Carousel description'

        class TestCarouselWidgetWithDescription(BaseTestCarouselWidget):
            description = caption

        with patch(
            'hammett.widgets.base.get_callback_query',
            return_value=SimpleNamespace(message=self.message),
        ):
            widget = TestCarouselWidgetWithDescription()
            await widget.move(self.update, self.context)
            await widget._next(self.update, self.context)

            expected = self.prepare_final_render_config(RenderConfig(
                description=caption,
                keyboard=await widget._build_keyboard(
                    self.update,
                    self.context,
                    # Since context.user_data is None, we can't get images attribute
                    # and use widget's default images instead
                    images=[],
                    current_image=0,
                ),
            ))
            self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

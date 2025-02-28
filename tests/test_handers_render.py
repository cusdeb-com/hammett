"""The module contains the tests for the render config which is generated in handlers."""

from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.core.hider import ONLY_FOR_ADMIN, Hider
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config, override_settings
from tests.base import BaseTestScreenWithDescription, TestScreen, TestStartScreen

_TEST_BUTTON_NAME = 'Test button'

_TEST_URL = 'https://github.com/cusdeb-com/hammett'


class BaseTestScreenWithDynamicDescription(Screen):
    """The class represents the base screen with a dynamic description for testing purposes."""

    DYNAMIC_DESCRIPTION = 'Test dynamic description'

    async def get_description(self, _update, _context) -> str:
        """Return the `DYNAMIC_DESCRIPTION` attribute of the screen."""
        return self.DYNAMIC_DESCRIPTION


class TestScreenWithDynamicAndStaticDescriptions(
    BaseTestScreenWithDescription,
    BaseTestScreenWithDynamicDescription,
):
    """The class represents the screen with both dynamic and static descriptions
    for testing purposes.
    """


class TestScreenWithDynamicDescription(BaseTestScreenWithDynamicDescription):
    """The class represents the screen with a dynamic description for testing purposes."""


class TestScreenWithSpecifiedHiderInKeyboard(BaseTestScreenWithDescription):
    """The class implements a screen for the tests with a specified hider in the keyboard."""

    async def add_default_keyboard(self, _update, _context):
        """Return a keyboard with the specified hider."""
        return [[
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourceTypes.URL_SOURCE_TYPE,
            ),
        ]]


class HandlersRenderTests(BaseTestCase):
    """The class contains tests for the render config generated through the handlers."""

    @catch_render_config()
    async def test_getting_description_on_move_when_both_types_of_description_are_set(self, actual):
        """Test calling the `move` handler to get the final render config that includes
        a dynamic description when the screen has both dynamic and static descriptions.
        """
        await TestScreenWithDynamicAndStaticDescriptions().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreenWithDynamicAndStaticDescriptions.DYNAMIC_DESCRIPTION,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_getting_dynamic_description_on_move(self, actual):
        """Test calling the `move` handler to get the final render config
        that includes a dynamic description.
        """
        await TestScreenWithDynamicDescription().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreenWithDynamicDescription.DYNAMIC_DESCRIPTION,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_screen_render_after_calling_jump_handler(self, actual):
        """Test calling the `jump` handler to get the final render config."""
        await TestScreen().jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=TestScreen.description,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await TestScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreen.description,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_screen_render_after_calling_send_handler(self, actual):
        """Test calling the `send` handler to get the final render config."""
        await TestScreen().send(self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=TestScreen.description,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await TestStartScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=TestStartScreen.description,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @override_settings(
        IS_ADMIN=False,
        HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker',
    )
    @catch_render_config()
    async def test_screen_render_with_specified_hider_in_keyboard(self, actual):
        """Test getting a final render config with a specified hider in the keyboard."""
        await TestScreenWithSpecifiedHiderInKeyboard().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=TestScreenWithSpecifiedHiderInKeyboard.description,
            keyboard=[[
                Button(
                    _TEST_BUTTON_NAME,
                    _TEST_URL,
                    hiders=Hider(ONLY_FOR_ADMIN),
                    source_type=SourceTypes.URL_SOURCE_TYPE,
                ),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

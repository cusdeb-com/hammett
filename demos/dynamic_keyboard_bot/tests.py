"""The module contains the tests for HammettDynamicKeyboard."""

# ruff: noqa: I001

import os
import unittest

from hammett.core.constants import RenderConfig
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import MAIN_MENU_SCREEN_DESCRIPTION, MainMenuScreen, request_dynamic_keyboard


class HammettDynamicKeyboardTests(BaseTestCase):
    """The class contains the tests for HammettDynamicKeyboard."""

    @catch_render_config()
    async def test_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=MAIN_MENU_SCREEN_DESCRIPTION,
            keyboard=request_dynamic_keyboard(MainMenuScreen().handle_button_click),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

"""The module contains the tests for HammettHideKeyboardBot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import NEXT_SCREEN_DESCRIPTION, START_SCREEN_DESCRIPTION, NextScreen, StartScreen


class HammettHideKeyboardBotTests(BaseTestCase):
    """The class contains the tests for HammettHideKeyboardBot."""

    @catch_render_config()
    async def test_next_screen_render_after_calling_jump_handler(self, actual):
        """Test calling the `jump` handler to get the final render config."""
        await NextScreen().jump(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            hide_keyboard=True,
            description=NEXT_SCREEN_DESCRIPTION,
            keyboard=[[
                Button('⬅️ Back', StartScreen,
                       source_type=SourceTypes.JUMP_SOURCE_TYPE),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_start_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await StartScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            hide_keyboard=True,
            description=START_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('Next screen ➡️', NextScreen,
                       source_type=SourceTypes.JUMP_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/hide_keyboard_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

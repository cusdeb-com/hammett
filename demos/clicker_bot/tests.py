"""The module contains the tests for HammettClickerBot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import CLICKER_SCREEN_DESCRIPTION, ClickerScreen


class HammettClickerBotTests(BaseTestCase):
    """The class contains the tests for HammettClickerBot."""

    @catch_render_config()
    async def test_clicker_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await ClickerScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=CLICKER_SCREEN_DESCRIPTION.format(num=0),
            keyboard=[
                [Button('➕ 1', ClickerScreen().add_one_click,  # noqa: RUF001
                       source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/clicker_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_clicker_screen_render_after_using_add_one_click_handler(self, actual):
        """Test using the `add_one_click` handler to get the final render config."""
        self.context.user_data['clicks_num'] = 0

        await ClickerScreen().add_one_click(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=CLICKER_SCREEN_DESCRIPTION.format(num=1),
            keyboard=[
                [Button('➕ 1', ClickerScreen().add_one_click,  # noqa: RUF001
                       source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/clicker_bot',
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

"""The module contains the tests for HammettSayHelloBot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import HELLO_SCREEN_DESCRIPTION, START_SCREEN_DESCRIPTION, HelloScreen, StartScreen


class HammettSayHelloBotTests(BaseTestCase):
    """The class contains the tests for HammettSayHelloBot."""

    @catch_render_config()
    async def test_hello_screen_render_after_sending_say_hello_command(self, actual):
        """Test sending the `say_hello` command to get the final render config."""
        await HelloScreen().handle_typing_say_hello_command(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=HELLO_SCREEN_DESCRIPTION,
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_start_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await StartScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=START_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/say_hello_bot',
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

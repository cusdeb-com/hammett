"""The module contains the tests for HammettJinja2Bot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import StartScreen


class HammettJinja2BotTests(BaseTestCase):
    """The class contains the tests for HammettJinja2Bot."""

    @catch_render_config()
    async def test_start_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await StartScreen().start(self.update, self.context)

        description = (
            'Welcome to <b>HammettJinja2Bot</b>! 🎨\n'
            '\n'
            'This demo shows how to use <b>Jinja2 templates</b> for dynamic descriptions. '
            'It uses a <b>for loop</b> to render a list of demos below. '
            'You can explore more features in the '
            '<a href="https://jinja.palletsprojects.com/">Jinja2 documentation</a>.\n'
            '\n'
            '<b>Live Demos:</b>\n'
            '1. <a href="https://t.me/HammettAdminPanelBot">AdminPanelBot</a>\n'
            '2. <a href="https://t.me/HammettCarouselBot">CarouselBot</a>\n'
            '3. <a href="https://t.me/HammettClickerBot">ClickerBot</a>\n'
            '4. <a href="https://t.me/HammettDynamicKeyboardBot">DynamicKeyboardBot</a>\n'
            '5. <a href="https://t.me/HammettHideKeyboardBot">HideKeyboardBot</a>\n'
            '6. <a href="https://t.me/HammettMultiStateBot">MultiStateBot</a>\n'
            '7. <a href="https://t.me/HammettPaywallBot">PaywallBot</a>\n'
            '8. <a href="https://t.me/HammettQuizBot">QuizBot</a>\n'
            '9. <a href="https://t.me/HammettReminderBot">ReminderBot</a>\n'
            '10. <a href="https://t.me/HammettSayHelloBot">SayHelloBot</a>\n'
            '11. <a href="https://t.me/HammettSimpleJumpBot">SimpleJumpBot</a>\n'
        )

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=description,
            keyboard=[
                [Button(
                    '📄 Source Code',
                    'https://github.com/cusdeb-com/hammett/tree/main/demos/jinja2_bot',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button(
                    '🎸 Hammett Homepage',
                    'https://github.com/cusdeb-com/hammett',
                    source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

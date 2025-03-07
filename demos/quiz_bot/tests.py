"""The module contains the tests for HammettQuizBot."""

# ruff: noqa: I001

import gettext
import json
import os
import unittest
from pathlib import Path

from hammett.conf import settings
from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config
from hammett.utils.translation import gettext as _

from screens import LanguageSwitcherScreen, MainMenuScreen


class HammettQuizBotTests(BaseTestCase):
    """The class contains the tests for HammettQuizBot."""

    def setUp(self):
        """Initialize questions from the file for testing."""
        gettext.textdomain(settings.DOMAIN)
        gettext.bindtextdomain(settings.DOMAIN, settings.LOCALE_PATH)

        with Path.open(settings.BASE_DIR / 'questions.json') as file:
            self.questions = json.loads(file.read())

    @catch_render_config()
    async def test_en_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=_(MainMenuScreen.caption),
            hide_keyboard=True,
            keyboard=[
                [Button(_('❓ Start Quiz'), MainMenuScreen().start_quiz_handler,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button(_('🌍 Language'), LanguageSwitcherScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button(_('📄 Source Code'),
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/quiz_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_pt_br_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        self.context.user_data['language_code'] = 'pt-br'

        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=_(MainMenuScreen.caption, 'pt-br'),
            hide_keyboard=True,
            keyboard=[
                [Button(_('❓ Start Quiz', 'pt-br'), MainMenuScreen().start_quiz_handler,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button(_('🌍 Language', 'pt-br'), LanguageSwitcherScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button(_('📄 Source Code', 'pt-br'),
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/quiz_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_ru_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        self.context.user_data['language_code'] = 'ru'

        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=_(MainMenuScreen.caption, 'ru'),
            hide_keyboard=True,
            keyboard=[
                [Button(_('❓ Start Quiz', 'ru'), MainMenuScreen().start_quiz_handler,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button(_('🌍 Language', 'ru'), LanguageSwitcherScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button(_('📄 Source Code', 'ru'),
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/quiz_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')

    unittest.main()

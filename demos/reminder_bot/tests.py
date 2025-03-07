"""The module contains the tests for HammettReminderBot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from screens import (
    MAIN_MENU_SCREEN_ADDITIONAL_DESCRIPTION,
    MAIN_MENU_SCREEN_DESCRIPTION,
    REMINDER_SCREEN_DESCRIPTION,
    SETTING_REMINDER_SCREEN_DESCRIPTION,
    MainMenuScreen,
    SettingReminderScreen,
    send_reminder,
)


class HammettReminderBotTests(BaseTestCase):
    """The class contains the tests for HammettReminderBot."""

    @catch_render_config()
    async def test_main_menu_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await MainMenuScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=MAIN_MENU_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('⏱️ Set Reminder', SettingReminderScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/reminder_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""
        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=MAIN_MENU_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('⏱️ Set Reminder', SettingReminderScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/reminder_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_main_menu_render_after_calling_move_handler_with_remind_set(self, actual):
        """Test calling the `move` handler to get the final render config."""
        self.context.chat_data['remind_is_set'] = True
        self.context.chat_data['seconds'] = 1

        await MainMenuScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=(
                MAIN_MENU_SCREEN_DESCRIPTION +
                MAIN_MENU_SCREEN_ADDITIONAL_DESCRIPTION.format(seconds=1)
            ),
            keyboard=[
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/reminder_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_main_menu_render_after_calling_start_handler_with_remind_set(self, actual):
        """Test calling the `start` handler to get the final render config with a set reminder."""
        self.context.chat_data['remind_is_set'] = True
        self.context.chat_data['seconds'] = 1

        await MainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=(
                MAIN_MENU_SCREEN_DESCRIPTION +
                MAIN_MENU_SCREEN_ADDITIONAL_DESCRIPTION.format(seconds=1)
            ),
            keyboard=[
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/reminder_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_reminder_screen_render_after_calling_send_reminder_handler(self, actual):
        """Test calling the `send_reminder` handler to get the final render config."""
        self.context.chat_data['remind_is_set'] = True
        self.context.chat_data['seconds'] = 1

        await send_reminder(self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=REMINDER_SCREEN_DESCRIPTION,
            keyboard=[[Button(
                '🏠 Main Menu', MainMenuScreen, source_type=SourceTypes.JUMP_SOURCE_TYPE),
            ]],
        ))
        self.assertFalse(self.context.chat_data['remind_is_set'])
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)
        with self.assertRaises(KeyError):
            self.context.chat_data['seconds']

    @catch_render_config()
    async def test_setting_reminder_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await SettingReminderScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=SETTING_REMINDER_SCREEN_DESCRIPTION,
            keyboard=await SettingReminderScreen().add_default_keyboard(self.update, self.context),
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

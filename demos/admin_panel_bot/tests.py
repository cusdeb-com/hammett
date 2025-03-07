"""The module contains the tests for HammettAdminPanelBot."""

# ruff: noqa: I001

import os
import unittest

from hammett.core import Button
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.core.hider import ONLY_FOR_ADMIN, Hider
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from screens import (
    ADMIN_PANEL_SCREEN_DESCRIPTION,
    MAIN_MENU_SCREEN_DESCRIPTION,
    NOT_ADMIN_CONFIRMATION_SCREEN_DESCRIPTION,
    AdminPanelScreen,
    MainMenuScreen,
    NotAdminConfirmationScreen,
)

_TEST_NAME = 'Hammett'


class HammettAdminPanelBotTests(BaseTestCase):
    """The class contains the tests for HammettAdminPanelBot."""

    @catch_render_config()
    async def test_admin_panel_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await AdminPanelScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=ADMIN_PANEL_SCREEN_DESCRIPTION,
            keyboard=[
                [Button("⚠️ I'm not an admin!", NotAdminConfirmationScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE, hiders=Hider(ONLY_FOR_ADMIN))],
                [Button('⬅️ Main Menu', MainMenuScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE, hiders=Hider(ONLY_FOR_ADMIN))],
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
                [Button('👑 Admin Panel', AdminPanelScreen, hiders=Hider(ONLY_FOR_ADMIN),
                        source_type=SourceTypes.MOVE_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/admin_panel_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_not_admin_confirmation_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""
        await NotAdminConfirmationScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=NOT_ADMIN_CONFIRMATION_SCREEN_DESCRIPTION,
            keyboard=[[
                Button('✅ Yes', NotAdminConfirmationScreen().exclude_from_admin_group,
                        source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                        hiders=Hider(ONLY_FOR_ADMIN)),
                Button('❌ No', MainMenuScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE, hiders=Hider(ONLY_FOR_ADMIN)),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

"""The module contains the tests for HammettPaywallBot.

When testing the permission mechanism, it's necessary for each test
to have its own screen classes. Otherwise, all tests will share the same
screens since screens are singletons.
"""

# ruff: noqa: I001

import os
import unittest

from hammett.conf import settings
from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.permission import ignore_permissions
from hammett.test.base import BaseTestCase
from hammett.test.utils import catch_render_config

from demo import (
    FAKE_PAYMENT_SCREEN_DESCRIPTION,
    MAIN_MENU_SCREEN_DESCRIPTION,
    PAYMENT_SCREEN_DESCRIPTION,
    FakePaymentScreen,
    MainMenuScreen,
    PaymentScreen,
)
from permissions import PaywallPermission


def _get_bot(entry_point, *screens):
    """Return a bot for testing purposes."""
    return Bot(
        'TestHammettPaywallBot',
        entry_point=entry_point,
        states={
            DEFAULT_STATE: {entry_point, *screens},
        },
    )


class HammettPaywallBotBotTests(BaseTestCase):
    """The class contains the tests for HammettPaywallBot."""

    def setUp(self):
        """Reset the `PAID_USERS` attribute."""
        settings.PAID_USERS = []

    @catch_render_config()
    async def test_fake_payment_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""

        class TestMainMenuScreen(StartMixin):
            """The class implements TestMainMenuScreen."""

            description = MAIN_MENU_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [
                    [Button('💸 Fake Refund', self.handle_fake_refund,
                        source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                    [Button('📄 Source Code',
                            'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                    [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                ]

            @register_button_handler
            async def handle_fake_refund(self, update, context):
                """Handle a button click and process a fake refund."""
                settings.PAID_USERS = []

                return await PaymentScreen().move(update, context)

        class TestFakePaymentScreen(Screen):
            """The class implements FakePaymentScreen."""

            description = FAKE_PAYMENT_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [[
                    Button('❌ No', PaymentScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE),
                    Button('✅ Yes', self.handle_fake_payment,
                        source_type=SourceTypes.HANDLER_SOURCE_TYPE),
                ]]

            @ignore_permissions([PaywallPermission])
            @register_button_handler
            async def handle_fake_payment(self, update, context):
                """Handle a button click and process a fake payment."""
                user = update.effective_user
                settings.PAID_USERS.append(user.id)

                return await MainMenuScreen().move(update, context)

            @ignore_permissions([PaywallPermission])
            async def move(self, update, context, **kwargs):
                """Switch to the screen re-rendering the previous message."""
                return await FakePaymentScreen().move(update, context, **kwargs)

        # The bot needs to be initialized for the permissions
        # to be applied to the screens.
        _get_bot(TestMainMenuScreen, TestFakePaymentScreen)

        await TestFakePaymentScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=FAKE_PAYMENT_SCREEN_DESCRIPTION,
            keyboard=[[
                Button('❌ No', PaymentScreen,
                    source_type=SourceTypes.MOVE_SOURCE_TYPE),
                Button('✅ Yes', FakePaymentScreen().handle_fake_payment,
                    source_type=SourceTypes.HANDLER_SOURCE_TYPE),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_main_menu_screen_render_after_calling_handle_fake_payment_handler(self, actual):
        """Test calling the `handle_fake_payment` handler to get the final render config."""

        class TestMainMenuScreen(StartMixin):
            """The class implements TestMainMenuScreen."""

            description = MAIN_MENU_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [
                    [Button('💸 Fake Refund', self.handle_fake_refund,
                        source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                    [Button('📄 Source Code',
                            'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                    [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                ]

            @register_button_handler
            async def handle_fake_refund(self, update, context):
                """Handle a button click and process a fake refund."""
                settings.PAID_USERS = []

                return await PaymentScreen().move(update, context)

        class TestFakePaymentScreen(Screen):
            """The class implements FakePaymentScreen."""

            description = FAKE_PAYMENT_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [[
                    Button('❌ No', PaymentScreen,
                        source_type=SourceTypes.MOVE_SOURCE_TYPE),
                    Button('✅ Yes', self.handle_fake_payment,
                        source_type=SourceTypes.HANDLER_SOURCE_TYPE),
                ]]

            @ignore_permissions([PaywallPermission])
            @register_button_handler
            async def handle_fake_payment(self, update, context):
                """Handle a button click and process a fake payment."""
                user = update.effective_user
                settings.PAID_USERS.append(user.id)

                return await MainMenuScreen().move(update, context)

            @ignore_permissions([PaywallPermission])
            async def move(self, update, context, **kwargs):
                """Switch to the screen re-rendering the previous message."""
                return await FakePaymentScreen().move(update, context, **kwargs)

        # The bot needs to be initialized for the permissions
        # to be applied to the screens.
        _get_bot(TestMainMenuScreen, TestFakePaymentScreen)

        await TestFakePaymentScreen().handle_fake_payment(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=MAIN_MENU_SCREEN_DESCRIPTION,
            keyboard=[
                [Button('💸 Fake Refund', MainMenuScreen().handle_fake_refund,
                       source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                [Button('📄 Source Code',
                        'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
                [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                        source_type=SourceTypes.URL_SOURCE_TYPE)],
            ],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_main_menu_screen_render_after_calling_start_handler(self, actual):
        """Test calling the `start` handler to get the final render config."""

        class TestMainMenuScreen(StartMixin):
            """The class implements TestMainMenuScreen."""

            description = MAIN_MENU_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [
                    [Button('💸 Fake Refund', self.handle_fake_refund,
                           source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                    [Button('📄 Source Code',
                            'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                    [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                ]

            @register_button_handler
            async def handle_fake_refund(self, update, context):
                """Handle a button click and process a fake refund."""
                settings.PAID_USERS = []

                return await PaymentScreen().move(update, context)

        class TestPaymentScreen(Screen):
            """The class implements TestPaymentScreen."""

            description = PAYMENT_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [[
                    Button('💳 Fake Pay', FakePaymentScreen,
                           source_type=SourceTypes.MOVE_SOURCE_TYPE),
                ]]

            @ignore_permissions([PaywallPermission])
            async def move(self, update, context, **kwargs):
                """Switch to the screen re-rendering the previous message."""
                return await PaymentScreen().move(update, context, **kwargs)

        # The bot needs to be initialized for the permissions
        # to be applied to the screens.
        _get_bot(TestMainMenuScreen, TestPaymentScreen)

        await TestMainMenuScreen().start(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            as_new_message=True,
            description=PAYMENT_SCREEN_DESCRIPTION,
            keyboard=[[
                Button('💳 Fake Pay', FakePaymentScreen,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)

    @catch_render_config()
    async def test_payment_screen_render_after_calling_move_handler(self, actual):
        """Test calling the `move` handler to get the final render config."""

        class TestMainMenuScreen(StartMixin):
            """The class implements TestMainMenuScreen."""

            description = MAIN_MENU_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [
                    [Button('💸 Fake Refund', self.handle_fake_refund,
                           source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
                    [Button('📄 Source Code',
                            'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                    [Button('🎸 Hammett Homepage', 'https://github.com/cusdeb-com/hammett',
                            source_type=SourceTypes.URL_SOURCE_TYPE)],
                ]

            @register_button_handler
            async def handle_fake_refund(self, update, context):
                """Handle a button click and process a fake refund."""
                settings.PAID_USERS = []

                return await PaymentScreen().move(update, context)

        class TestPaymentScreen(Screen):
            """The class implements TestPaymentScreen."""

            description = PAYMENT_SCREEN_DESCRIPTION

            async def add_default_keyboard(self, _update, _context):
                """Set up the keyboard for the screen."""
                return [[
                    Button('💳 Fake Pay', FakePaymentScreen,
                           source_type=SourceTypes.MOVE_SOURCE_TYPE),
                ]]

            @ignore_permissions([PaywallPermission])
            async def move(self, update, context, **kwargs):
                """Switch to the screen re-rendering the previous message."""
                return await PaymentScreen().move(update, context, **kwargs)

        # The bot needs to be initialized for the permissions
        # to be applied to the screens.
        _get_bot(TestMainMenuScreen, TestPaymentScreen)

        await TestPaymentScreen().move(self.update, self.context)

        expected = self.prepare_final_render_config(RenderConfig(
            description=PAYMENT_SCREEN_DESCRIPTION,
            keyboard=[[
                Button('💳 Fake Pay', FakePaymentScreen,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ]],
        ))
        self.assertFinalRenderConfigEqual(expected, actual.final_render_config)


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')

    unittest.main()

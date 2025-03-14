"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.conf import settings
from hammett.core import Bot, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.permission import ignore_permissions
from hammett.core.persistence import RedisPersistence

from permissions import PaywallPermission

MAIN_MENU_SCREEN_DESCRIPTION = (
    "Congratulations! You've successfully made a fake payment. Now you can see the "
    "<b>Main Menu</b> screen even after typing the /start command.\n"
    "\n"
    "<i>If you'd like to try the demo again, just click the button below "
    "to make a fake refund 👇</i>"
)

FAKE_PAYMENT_SCREEN_DESCRIPTION = (
    'To continue using the bot, you need to make a <i>fake</i> payment.\n'
    '\n'
    'Do you want to continue?'
)

PAYMENT_SCREEN_DESCRIPTION = (
    "Welcome to HammettPaywallBot!\n"
    "\n"
    "Now you see the <b>Payment</b> screen, and you <i>won't see any other screens</i> until "
    "you make a <i>fake</i> payment. So, if you type the /start command, "
    "you'll just get this screen again."
)


class FakePaymentScreen(Screen):
    """The class implements FakePaymentScreen."""

    description = FAKE_PAYMENT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                '❌ No',
                PaymentScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE),
            Button(
                '✅ Yes',
                self.handle_fake_payment,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE),
        ]]

    @ignore_permissions([PaywallPermission])
    @register_button_handler
    async def handle_fake_payment(self, update, context):
        """Handle a button click and process a fake payment.

        Please note that this handler ignores `PaywallPermission`,
        which means that `has_permission` of `PaywallPermission`
        is not called before it is invoked.
        """
        user = update.effective_user
        settings.PAID_USERS.append(user.id)

        return await MainMenuScreen().move(update, context)

    @ignore_permissions([PaywallPermission])
    async def move(self, update, context, **kwargs):
        """Switch to the screen re-rendering the previous message.

        Please note that this handler ignores `PaywallPermission`,
        which means that `has_permission` of `PaywallPermission`
        is not called before it is invoked.
        """
        return await super().move(update, context, **kwargs)


class MainMenuScreen(StartMixin):
    """The class implements MainMenuScreen, which is only available after a fake payment."""

    description = MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [
            [Button(
                '💸 Fake Refund',
                self.handle_fake_refund,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE)],
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/paywall_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]

    @register_button_handler
    async def handle_fake_refund(self, update, context):
        """Handle a button click and process a fake refund."""
        settings.PAID_USERS = []

        return await PaymentScreen().move(update, context)


class PaymentScreen(Screen):
    """The class implements PaymentScreen, which appears when the user hasn't made a payment."""

    description = PAYMENT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the keyboard for the screen."""
        return [[
            Button(
                '💳 Fake Pay',
                FakePaymentScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE),
        ]]

    @ignore_permissions([PaywallPermission])
    async def move(self, update, context, **kwargs):
        """Switch to the screen re-rendering the previous message.

        Please note that this handler ignores `PaywallPermission`,
        which means that `has_permission` of `PaywallPermission`
        is not called before it is invoked.
        """
        return await super().move(update, context, **kwargs)


def main():
    """Run the bot."""
    bot = Bot(
        'HammettPaywallBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {FakePaymentScreen, MainMenuScreen, PaymentScreen},
        },
    )
    bot.run()


if __name__ == '__main__':
    main()

"""The bot is designed to demonstrate how to use permissions."""

from demos.paywall.permissions import PaywallPermission
from hammett.conf import settings
from hammett.core import Application, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.permissions import ignore_permissions
from hammett.core.screen import StartScreen


class PayScreen(Screen):
    """Class displayed if the user has not paid."""

    description = 'You have to pay to continue'

    def setup_keyboard(self):
        """Sets up the keyboard for the screen."""

        return [
            [Button(
                'Fake payment',
                self.handle_fake_payment,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            )],
            [Button(
                'Try to skip',
                self.handle_try_skip,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            )],
        ]

    @register_button_handler
    async def handle_try_skip(self, update, context):
        """Handles a button click and tries to redirect to the main menu."""

        return await MainMenu().goto(update, context)

    @ignore_permissions([PaywallPermission])
    @register_button_handler
    async def handle_fake_payment(self, update, context):
        """Handles a button click and processes a fake payment."""

        user = update.effective_user
        settings.PAID_USERS.append(user.id)
        return await MainMenu().goto(update, context)


class MainMenu(StartScreen):
    """A screen that is only available after payment."""

    description = 'This screen is only available after payment'

    def setup_keyboard(self):
        """Sets up the keyboard for the screen."""

        return [[
            Button(
                'Reset',
                self.handle_reset_payment,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            ),
        ]]

    @register_button_handler
    async def handle_reset_payment(self, update, context):
        """Handles a button click and resets the payment."""

        settings.PAID_USERS = []
        return await PayScreen().jump(update, context)


def main():
    """Runs the bot. """

    name = 'permissions'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: [MainMenu, PayScreen],
        },
    )
    app.run()


if __name__ == '__main__':
    main()

"""The module contains PaywallPermission."""

from hammett.conf import settings
from hammett.core.permissions import Permission


class PaywallPermission(Permission):
    """A class that implements active user payment verification."""

    async def has_permission(self, update, context):
        """Checks if the user has paid for access to the bot."""

        user = update.effective_user
        return user.id in settings.PAID_USERS

    async def handle_permission_denied(self, update, context):
        """Redirects to the payment screen."""

        from demos.paywall.demo import PayScreen
        return await PayScreen().jump(update, context)

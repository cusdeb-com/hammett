"""The module contains implementation of PaywallPermission."""

from hammett.conf import settings
from hammett.core.permission import Permission


class PaywallPermission(Permission):
    """The class implements active user payment verification."""

    async def has_permission(self, update, _context):
        """Check if the user has paid for access to the bot. If the check
        isn't successful, the `handle_permission_denied` method will be called.
        """
        user = update.effective_user
        return user.id in settings.PAID_USERS

    async def handle_permission_denied(self, update, context):
        """Redirect to the payment screen after a failed check of
        the `has_permission` method.
        """
        from demo import PaymentScreen

        return await PaymentScreen().jump(update, context)

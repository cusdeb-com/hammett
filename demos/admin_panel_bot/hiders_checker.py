"""The module contains the hiders checker for the bot."""

from hammett.conf import settings
from hammett.core.hider import HidersChecker


class DemoHidersChecker(HidersChecker):
    """The class implements DemoHidersChecker to control the visibility
    of the buttons of the screens.
    """

    async def is_admin(self, update, _context):
        """Return the result of checking whether the user is an admin."""
        user = update.effective_user
        return user.id in settings.ADMIN_GROUP

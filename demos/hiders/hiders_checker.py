"""The module contains the hiders checker for the bot. """

from hammett.conf import settings
from hammett.core.hider import HidersChecker


class DemoHidersChecker(HidersChecker):
    async def is_admin(self, update, _context) -> bool:
        user = update.effective_user
        return user.id in settings.ADMIN_GROUP

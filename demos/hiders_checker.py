"""The module contains the hiders checker for the bot. """

from hammett.conf import settings
from hammett.core.hiders import HidersChecker


class DemoHidersChecker(HidersChecker):
    async def is_admin(self, context) -> bool:
        user_id = self.get_user_id_from_context(context)
        return user_id in settings.ADMIN_GROUP

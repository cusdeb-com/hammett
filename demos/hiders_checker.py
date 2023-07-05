"""The module contains the hiders checker for the bot. """

from hammett.conf import settings
from hammett.core.hiders import HidersChecker


class DemoHidersChecker(HidersChecker):
    async def is_admin(self, update, context) -> bool:
        try:
            user = update.message.from_user
        except AttributeError:
            query = update.callback_query
            await query.answer()

            user = update.effective_chat

        return user.id in settings.ADMIN_GROUP

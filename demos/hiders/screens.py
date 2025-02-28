"""The module contains the screens the bot consists of."""

import logging

from hammett.conf import settings
from hammett.core import Button, Screen
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.hider import ONLY_FOR_ADMIN, Hider
from hammett.core.mixins import StartMixin

LOGGER = logging.getLogger('hammett')


class NotAdminConfirmation(Screen):
    """The class implements the NotAdminConfirmation screen."""

    description = 'Are you sure you want to remove yourself from the admin group?'

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [
                Button('✅ Yes', self.exclude_user_from_admin_group),
                Button('⬅️ Main Menu', MainMenu,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
        ]

    @staticmethod
    @register_button_handler
    async def exclude_user_from_admin_group(update, context):
        """Handle an excluding of the user from the admin group."""
        main_menu = MainMenu()
        user = update.effective_user

        settings.ADMIN_GROUP.remove(user.id)

        await main_menu.move(update, context)
        return DEFAULT_STATE


class MainMenu(StartMixin, Screen):
    """The class implements the MainMenu screen."""

    admin_status = 'admin'
    anonymous_status = 'anonymous'
    greeting = 'Hello, <b>{user_status}</b>!'
    text_map = {
        admin_status: (
            f'{greeting}\n\n'
            f'Your status allows you to see all the buttons of the main menu.'
        ),
        anonymous_status: (
            f'{greeting}\n\n'
            f"Your status doesn't allow you to see the hidden buttons of the main menu."
        ),
    }

    #
    # Private methods
    #

    async def _get_user_status(self, user_id):
        if user_id in settings.ADMIN_GROUP:
            return self.admin_status

        return self.anonymous_status

    #
    # Public methods
    #

    async def get_config(self, update, _context, **_kwargs):
        """Return the config of the screen."""
        user = update.effective_user
        user_status = await self._get_user_status(user.id)
        description = self.text_map[user_status].format(user_status=user_status)

        config = RenderConfig()
        config.description = description

        return config

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [
                Button('🔒 Available only for admins', SecretRoom,
                       hiders=Hider(ONLY_FOR_ADMIN),
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
            [
                Button("❌ I'm not an admin!", NotAdminConfirmation,
                       hiders=Hider(ONLY_FOR_ADMIN),
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
            [
                Button('🎸 Hammett Home Page', 'https://github.com/cusdeb-com/hammett',
                       source_type=SourceTypes.URL_SOURCE_TYPE),
            ],
        ]

    async def start(self, update, context):
        """Reply to the /start command."""
        try:
            user = update.message.from_user
        except AttributeError:
            # When the start handler is invoked through editing
            # the message with the /start command.
            user = update.edited_message.from_user

        settings.ADMIN_GROUP.append(user.id)
        LOGGER.info('The user %s (%s) was added to the admin group.', user.username, user.id)

        return await super().start(update, context)


class SecretRoom(Screen):
    """The class implements the SecretRoom screen."""

    description = 'This is the secret room available only for admins.'

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [
                Button('⬅️ Main Menu', MainMenu,
                       source_type=SourceTypes.MOVE_SOURCE_TYPE),
            ],
        ]

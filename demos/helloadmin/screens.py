"""The module contains the screens the bot consists of. """

import logging

from hammett.conf import settings
from hammett.core.constants import DEFAULT_STAGE, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.hiders import ONLY_FOR_ADMIN, Hider
from hammett.core.screen import Button, RenderConfig, Screen, StartScreen

LOGGER = logging.getLogger('hammett')


class NotAdminConfirmation(Screen):
    description = 'Are you sure you want to remove yourself from the admin group?'

    def setup_keyboard(self):
        return [
            [
                Button('✅ Yes', self.exclude_user_from_admin_group),
                Button('⬅️ Main Menu', MainMenu,
                       source_type=SourcesTypes.GOTO_SOURCE_TYPE),
            ],
        ]

    @staticmethod
    @register_button_handler
    async def exclude_user_from_admin_group(update, context):
        main_menu = MainMenu()
        user = update.effective_user

        settings.ADMIN_GROUP.remove(user.id)

        await main_menu.render(update, context)
        return DEFAULT_STAGE


class MainMenu(StartScreen):
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

    async def render(
        self,
        update,
        context,
        *,
        config: 'RenderConfig | None' = None,
    ):
        user = update.effective_user
        user_status = await self._get_user_status(user.id)
        description = self.text_map[user_status].format(user_status=user_status)

        config = config or RenderConfig()
        config.description = description
        await super().render(
            update,
            context,
            config=config,
        )

    def setup_keyboard(self):
        return [
            [
                Button('🔒 Available only for admins', SecretRoom,
                       hiders=Hider(ONLY_FOR_ADMIN),
                       source_type=SourcesTypes.GOTO_SOURCE_TYPE),
            ],
            [
                Button("❌ I'm not an admin!", NotAdminConfirmation,
                       hiders=Hider(ONLY_FOR_ADMIN),
                       source_type=SourcesTypes.GOTO_SOURCE_TYPE),
            ],
            [
                Button('🎸 Hammett Home Page', 'https://github.com/cusdeb-com/hammett',
                       source_type=SourcesTypes.URL_SOURCE_TYPE),
            ],
        ]

    async def start(self, update, context):
        """Replies to the /start command. """

        try:
            user = update.message.from_user
        except AttributeError:
            # When the start handler is invoked through editing
            # the message with the /start command.
            user = update.edited_message.from_user

        settings.ADMIN_GROUP.append(user.id)
        LOGGER.info('The user %s (%s) was added to the admin group.', user.username, user.id)

        config = RenderConfig(as_new_message=True)
        await self.render(update, context, config=config)
        return DEFAULT_STAGE


class SecretRoom(Screen):
    description = 'This is the secret room available only for admins.'

    def setup_keyboard(self):
        return [
            [
                Button('⬅️ Main Menu', MainMenu,
                       source_type=SourcesTypes.GOTO_SOURCE_TYPE),
            ],
        ]

"""The module is a script for running the bot."""

from hammett.core import Button, Screen
from hammett.core.constants import RenderConfig, SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin

MAIN_MENU_SCREEN_DESCRIPTION = (
    'Welcome to HammettReminderBot!\n'
    '\n'
    'This bot helps you remember to <i>buy milk</i> by setting reminders. '
    'Just press <b>⏱️ Set Reminder</b>.'
)

MAIN_MENU_SCREEN_ADDITIONAL_DESCRIPTION = (
    "\n\n"
    "You've set a reminder! It'll be here in <b>{seconds} sec</b>."
)

REMINDER_SCREEN_DESCRIPTION = 'Alarm! You need to buy milk!'

SETTING_REMINDER_SCREEN_DESCRIPTION = 'Here you can set a reminder.'


class MainMenuScreen(StartMixin, Screen):
    """The class implements MainMenuScreen."""

    async def add_default_keyboard(self, _update, context):
        """Set up the default keyboard for the screen."""
        keyboard = []
        if not context.chat_data.get('remind_is_set'):
            keyboard.append([Button(
                '⏱️ Set Reminder',
                SettingReminderScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE)],
            )

        keyboard.extend([
            [Button(
                '📄 Source Code',
                'https://github.com/cusdeb-com/hammett/tree/main/demos/reminder_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ])
        return keyboard

    async def get_description(self, _update, context):
        """Return the screen description based on the reminder status."""
        description = MAIN_MENU_SCREEN_DESCRIPTION
        if context.chat_data.get('seconds'):
            description += MAIN_MENU_SCREEN_ADDITIONAL_DESCRIPTION.format(
                seconds=context.chat_data['seconds'],
            )

        return description


class ReminderScreen(Screen):
    """The class implements Screen, which acts as a notification."""

    description = REMINDER_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '🏠 Main Menu',
                MainMenuScreen,
                source_type=SourceTypes.JUMP_SOURCE_TYPE),
        ]]


class SettingReminderScreen(Screen):
    """The class implements SettingReminderScreen."""

    description = SETTING_REMINDER_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        time_keyboard = [
            [Button(
                f'⌛️ {time} sec',
                self.set_reminder,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
                payload=f'{time}',
            )] for time in (15, 30, 60)]

        time_keyboard.append([
            Button(
                '⬅️ Back',
                MainMenuScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE),
        ])
        return time_keyboard

    @register_button_handler
    async def set_reminder(self, update, context):
        """Handle a request for setting a reminder after a certain time."""
        context.chat_data['remind_is_set'] = True

        seconds = await self.get_payload(update, context)
        context.chat_data['seconds'] = seconds

        context.job_queue.run_once(
            send_reminder,
            when=int(seconds),
            chat_id=update.effective_chat.id,
        )

        return await MainMenuScreen().move(update, context)


async def send_reminder(context):
    """Send a reminder after a certain time."""
    await ReminderScreen().send(context, config=RenderConfig(chat_id=context._chat_id))  # noqa: SLF001

    context.chat_data['remind_is_set'] = False
    context.chat_data.pop('seconds', None)

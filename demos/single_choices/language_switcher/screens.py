"""The module contains the screens the bot consists of. """

from hammett.core.mixins import StartMixin
from hammett.utils.translation import gettext as _
from hammett.widgets import SingleChoiceWidget


class MainMenu(SingleChoiceWidget, StartMixin):
    """The class represents the main menu of the Language switcher demo bot."""

    choices = (
        ('en', 'English'),
        ('ru', 'Русский'),
        ('fr', 'Français'),
    )

    async def get_description(self, _update, context):
        """Returns the translated description of the screen."""

        language_code = context.user_data.get('language_code', 'en')
        return _('Main menu description', language_code)

    async def get_initial_value(self, update, context):
        """Returns the value selected by default."""

        language_code = context.user_data.get('language_code', None)
        if not language_code:
            return 'en'

        return language_code

    async def switch(self, update, context, selected_choice):
        """Saves the selected language."""

        selected_language, _ = selected_choice
        context.user_data['language_code'] = selected_language

        return await super().switch(update, context, selected_choice)

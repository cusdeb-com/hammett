"""The module contains the screens the bot consists of. """

from hammett.widgets import SingleChoiceWidget


class MainMenu(SingleChoiceWidget):
    choices = (
        ('1', 'First choice'),
        ('2', 'Second choice'),
    )
    initial_value = '1'
    description = 'Single choice'

    async def start(self, update, context):
        return await self.jump(update, context)

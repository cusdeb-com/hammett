"""The module contains the screens the bot consists of."""

from hammett.widgets import MultiChoiceWidget


class MainMenu(MultiChoiceWidget):
    choices = (
        ('1', 'First choice'),
        ('2', 'Second choice'),
    )
    initial_values = ('1',)
    description = 'Multi choice'

    async def start(self, update, context):
        return await self.jump(update, context)

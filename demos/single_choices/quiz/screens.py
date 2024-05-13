"""The module contains the screens the bot consists of. """

import json

import aiofiles
from hammett.conf import settings
from hammett.core import Button, Screen
from hammett.core.constants import SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.widgets import SingleChoiceWidget


class MainMenu(StartMixin, Screen):
    """The class represents the main menu of the Quiz demo bot."""

    description = 'Press the button to start the quiz'

    async def add_default_keyboard(self, _update, _context):
        """Sets up the default keyboard for the screen."""

        return [[
            Button('Start quiz!', Quiz,
                   source_type=SourcesTypes.GOTO_SOURCE_TYPE),
        ]]

    async def render(self, update, context, *, config=None, extra_data=None):
        """Reset the index number of the last question and the number of correct answers."""

        context.user_data['question_index'] = context.user_data['correct_answers_num'] = 0
        return await super().render(update, context, config=config, extra_data=extra_data)

    async def start(self, update, context):
        """Sets the questions and their number to `context.user_data`."""

        async with aiofiles.open(settings.BASE_DIR / 'questions.json') as file:
            questions = json.loads(await file.read())

        context.user_data['questions'] = questions
        context.user_data['questions_num'] = len(questions) - 1

        return await super().start(update, context)


class Quiz(SingleChoiceWidget):
    """The class represents the screen with quiz questions."""

    async def add_extra_keyboard(self, _update, _context):
        """Sets up the default keyboard for the screen."""

        return [[
            Button('Next question', self.next_question,
                   source_type=SourcesTypes.HANDLER_SOURCE_TYPE),
        ]]

    async def get_description(self, _update, context):
        """Returns the `description` attribute of the screen."""

        index = context.user_data['question_index']
        questions = context.user_data['questions']
        return questions[index]['question']

    async def get_choices(self, _update, context, **_kwargs):
        """Returns the `choices` attribute of the widget."""

        index = context.user_data['question_index']
        questions = context.user_data['questions']

        result = []
        for i, answer in enumerate(questions[index]['answers']):
            result.append((i + 1, answer))

        return result

    async def switch(self, update, context, selected_choice):
        """Switches the widget from one state to another and check the answer."""

        answer, _ = selected_choice
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        if answer == questions[index]['correct_answer']:
            context.user_data['correct_answers_num'] += 1

        return await super().switch(update, context, selected_choice)

    @register_button_handler
    async def next_question(self, update, context):
        """Switches to the next question or to the screen with results of the quiz."""

        if context.user_data['questions_num'] <= context.user_data['question_index']:
            return await Result().goto(update, context)

        context.user_data['question_index'] += 1

        return await self.goto(update, context)


class Result(Screen):
    """The class represents the screen with results of the quiz."""

    async def get_description(self, update, context):
        """Returns the `description` attribute of the screen."""

        return (
            f"You've earned <b>{context.user_data['correct_answers_num']}</b>/"
            f"<b>{context.user_data['questions_num'] + 1}</b> scores"
        )

    async def add_default_keyboard(self, _update, _context):
        """Sets up the default keyboard for the screen."""

        return [[
            Button('Back to main menu', MainMenu,
                   source_type=SourcesTypes.GOTO_SOURCE_TYPE),
        ]]

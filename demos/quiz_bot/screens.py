"""The module contains the screens the bot consists of."""

import json
import random

import aiofiles

from hammett.conf import settings
from hammett.core import Button, Screen
from hammett.core.constants import SourceTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.utils.translation import gettext as _
from hammett.widgets import MultiChoiceWidget, SingleChoiceWidget
from hammett.widgets.base import BaseChoiceWidget

MAX_QUESTIONS_NUM = 5


class BaseScreen(Screen):
    """The base screen for all the screens in the bot."""

    hide_keyboard = True

    caption = ''

    async def get_description(self, _update, context):
        """Return the translated description of the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return _(self.caption, language_code)

    @staticmethod
    def get_next_choice_widget(next_correct_answer):
        """Return the widget screen based on the type of answer for the next question."""
        return (
            QuizMultiChoiceWidget
            if isinstance(next_correct_answer, list)
            else QuizSingleChoiceWidget
        )


class BaseQuizScreen(BaseScreen, BaseChoiceWidget):
    """The base screen for all the screens involved in the quiz."""

    async def add_extra_keyboard(self, _update, context):
        """Add an extra keyboard below the widget buttons."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(
                _('🏠 Main Menu', language_code),
                MainMenuScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE),
            Button(
                _('Next ➡️', language_code),
                self.next_question,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE),
        ]]

    async def get_choices(self, _update, context, **_kwargs):
        """Return the choices with the available answers to the question."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        result = [(answer, answer) for answer in questions[index]['answers']]
        random.shuffle(result)

        return tuple(result)

    async def get_description(self, _update, context):
        """Return the `description` attribute of the screen."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']
        language_code = context.user_data.get('language_code', 'en')

        return (
            f'№ <b>{index + 1} / {len(context.user_data["questions"])}.</b> '
            f'{questions[index]["question"][language_code]}'
        )

    @register_button_handler
    async def next_question(self, update, context):
        """Check the answer and switch to the next question or to the results
        screen for the completed quiz.
        """
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        if (
            # The list of selected answers must be sorted to match the correct answer
            isinstance(context.user_data['answer'], list) and
            sorted(context.user_data['answer']) == questions[index]['correct_answer']
        ) or (
            context.user_data['answer'] == questions[index]['correct_answer']
        ):
            context.user_data['correct_answers_num'] += 1

        context.user_data['question_index'] += 1

        try:  # Choose the type of the next widget screen or finish the quiz
            next_correct_answer = questions[context.user_data['question_index']]['correct_answer']
        except IndexError:
            return await ResultScreen().move(update, context)

        return await self.get_next_choice_widget(next_correct_answer)().move(update, context)


class LanguageSwitcherScreen(BaseScreen, SingleChoiceWidget):
    """The class implements LanguageSwitcherScreen."""

    choices = (
        ('en', '🇬🇧 English'),
        ('pt-br', '🇧🇷 Português'),
        ('ru', '🇷🇺 Русский'),
    )

    caption = 'language_switcher_screen'

    async def add_extra_keyboard(self, _update, context):
        """Add an extra keyboard below the widget buttons."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(
                _('⬅️ Back', language_code),
                MainMenuScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE),
        ]]

    async def get_initial_value(self, _update, context):
        """Return the updated or default language code."""
        language_code = context.user_data.get('language_code', 'en')
        if not language_code:
            return 'en'

        return language_code

    async def switch(self, update, context, selected_choice):
        """Save the selected language and re-render the screen."""
        selected_language, _ = selected_choice
        context.user_data['language_code'] = selected_language

        return await super().switch(update, context, selected_choice)


class MainMenuScreen(BaseScreen, StartMixin):
    """The class implements MainMenuScreen."""

    caption = 'main_menu_screen'

    async def add_default_keyboard(self, _update, context):
        """Set up the default keyboard for the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return [
            [Button(
                _('❓ Start Quiz', language_code),
                self.start_quiz_handler,
                source_type=SourceTypes.HANDLER_SOURCE_TYPE,
            )],
            [Button(
                _('🌍 Language', language_code),
                LanguageSwitcherScreen,
                source_type=SourceTypes.MOVE_SOURCE_TYPE,
            )],
            [Button(
                _('📄 Source Code', language_code),
                'https://github.com/cusdeb-com/hammett/tree/main/demos/quiz_bot',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Homepage',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourceTypes.URL_SOURCE_TYPE)],
        ]

    async def render(self, update, context, *, config=None, **kwargs):
        """Initialize or reset to prepare the questions for the quiz."""
        context.user_data['question_index'] = 0
        context.user_data['correct_answers_num'] = 0
        context.user_data['answer'] = 0

        context.user_data['questions'] = random.sample(
            context.user_data['all_questions'],
            k=MAX_QUESTIONS_NUM,
        )

        return await super().render(update, context, config=config, **kwargs)

    async def start(self, update, context):
        """Reply to the /start command, load and save the questions from the file."""
        async with aiofiles.open(settings.BASE_DIR / 'questions.json') as file:
            questions = json.loads(await file.read())
            context.user_data['all_questions'] = questions

        return await super().start(update, context)

    @register_button_handler
    async def start_quiz_handler(self, update, context):
        """Handle a request to start the quiz."""
        index = context.user_data['question_index']
        questions = context.user_data['questions']

        return await self.get_next_choice_widget(
            questions[index]['correct_answer'],
        )().move(update, context)


class QuizMultiChoiceWidget(BaseQuizScreen, MultiChoiceWidget):
    """The class implements QuizSingleChoiceWidget, which is used when
    a question has more than one correct answer.
    """

    async def switch(self, update, context, selected_choice):
        """Save the passed answer and re-render the screen with the updated emoji
        of the clicked button.
        """
        answer, _ = selected_choice
        if isinstance(context.user_data.get('answer'), list):
            if answer in context.user_data['answer']:  # Answer was canceled
                context.user_data['answer'].remove(answer)
            else:
                context.user_data['answer'].append(answer)
        else:
            context.user_data['answer'] = [answer]

        return await super().switch(update, context, selected_choice)


class QuizSingleChoiceWidget(BaseQuizScreen, SingleChoiceWidget):
    """The class implements QuizSingleChoiceWidget, which is used when
    a question has only one correct answer.
    """

    async def switch(self, update, context, selected_choice):
        """Save the passed answer and re-render the screen with the updated emoji
        of the clicked button.
        """
        answer, _ = selected_choice
        context.user_data['answer'] = answer

        return await super().switch(update, context, selected_choice)


class ResultScreen(BaseScreen):
    """The class implements ResultScreen."""

    caption = 'result_screen'

    async def add_default_keyboard(self, _update, context):
        """Set up the default keyboard for the screen."""
        language_code = context.user_data.get('language_code', 'en')
        return [[
            Button(_('🏠 Main Menu', language_code), MainMenuScreen,
                   source_type=SourceTypes.MOVE_SOURCE_TYPE),
        ]]

    async def get_description(self, update, context):
        """Return the `description` attribute of the screen."""
        template = await super().get_description(update, context)
        return template.format(
            correct_answers_num=context.user_data['correct_answers_num'],
            questions_num=len(context.user_data['questions']),
        )

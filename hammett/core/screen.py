from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ConversationHandler as NativeConversationHandler

from hammett.core.exceptions import (
    ImproperlyConfigured,
    UnknownSourceType,
)
from hammett.utils.module_loading import import_string

DEFAULT_STAGE = 0

(
    GOTO_SOURCE_TYPE,
    HANDLER_SOURCE_TYPE,
    URL_SOURCE_TYPE,
) = range(3)


class Button:
    hiders_checker = None

    def __init__(
            self,
            caption,
            source,
            *,
            source_type=HANDLER_SOURCE_TYPE,
            hiders=None,
    ):
        self.caption = caption
        self.source = source
        self.source_goto = source().goto if source_type == GOTO_SOURCE_TYPE else None
        self.source_wrapped = None
        self.source_type = source_type
        self.hiders = hiders

        if self.hiders and not self.hiders_checker:
            self._init_hider_checker()

    #
    # Private methods
    #

    def _init_hider_checker(self):
        from hammett.conf import settings

        if not settings.HIDERS_CHECKER:
            msg = "The 'HIDERS_CHECKER' setting is not set"
            raise ImproperlyConfigured(msg)

        hiders_checker = import_string(settings.HIDERS_CHECKER)
        self.hiders_checker = hiders_checker(self.hiders.hiders_set)

    async def _specify_visibility(self, update, context):
        visibility = True
        if self.hiders and not await self.hiders_checker.run(update, context):
            visibility = False

        return visibility

    #
    # Public methods
    #

    @staticmethod
    def create_handler_pattern(handler):
        return f'{type(handler.__self__).__name__}.{handler.__name__}'

    async def create(self, update, context):
        visibility = await self._specify_visibility(update, context)

        if self.source_type in (GOTO_SOURCE_TYPE, HANDLER_SOURCE_TYPE):
            source = self.source_goto if self.source_type == GOTO_SOURCE_TYPE else self.source

            pattern = self.create_handler_pattern(source)
            return InlineKeyboardButton(self.caption, callback_data=pattern), visibility

        if self.source_type == URL_SOURCE_TYPE:
            return InlineKeyboardButton(self.caption, url=self.source), visibility

        raise UnknownSourceType


class ConversationHandler(NativeConversationHandler):
    async def handle_update(
            self,
            update,
            dispatcher,
            check_result,
            context=None,
    ):
        try:
            res = await super().handle_update(update, dispatcher, check_result, context)
        except BadRequest as exc:  # noqa: TRY302
            raise exc  # noqa: TRY201
        else:
            return res


class Screen:
    html_parse_mode = DEFAULT_NONE
    text = None

    _instance = None

    def __init__(self):
        if self.html_parse_mode is DEFAULT_NONE:
            from hammett.conf import settings
            self.html_parse_mode = settings.HTML_PARSE_MODE

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    #
    # Private methods
    #

    @staticmethod
    async def _create_markup_keyboard(rows, update, context):
        keyboard = []
        for row in rows:
            buttons = []
            for button in row:
                inline_button, visible = await button.create(update, context)
                if visible:
                    buttons.append(inline_button)

            keyboard.append(buttons)

        return InlineKeyboardMarkup(keyboard)

    #
    # Public methods
    #

    @staticmethod
    async def get_callback_query(update):
        """Gets CallbackQuery from Update. """

        query = update.callback_query
        # CallbackQueries need to be answered, even if no notification to the user is needed.
        # Some clients may have trouble otherwise.
        # See https://core.telegram.org/bots/api#callbackquery
        await query.answer()
        return query

    async def goto(self, update, context):
        """Switches to the screen. """

        await self.render(update, context)
        return DEFAULT_STAGE

    async def render(
            self,
            update,
            context,
            *,
            as_new_message=False,
            keyboard=None,
            text=None,
    ):
        """Renders the screen components (i.e., text and keyboard). """

        keyboard = keyboard or self.setup_keyboard()
        text = text or self.text

        kwargs = {}
        if as_new_message:
            chat_id = update.effective_chat.id
            kwargs['chat_id'] = chat_id
            send = context.bot.send_message
        else:
            query = await self.get_callback_query(update)
            send = query.edit_message_text

        await send(
            parse_mode=ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
            reply_markup=await self._create_markup_keyboard(keyboard, update, context),
            text=text,
            **kwargs,
        )

    def setup_keyboard(self):
        """Sets up the keyboard for the screen. """

        return []

    async def start(self, update, context):
        raise NotImplemented

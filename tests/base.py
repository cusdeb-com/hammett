"""The module contains the classes for the Hammett tests."""

import datetime
from abc import ABC

from telegram import Chat, Message
from telegram.constants import ChatType

from hammett.core import Bot
from hammett.core.constants import DEFAULT_STATE
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.permission import Permission
from hammett.core.renderer import Renderer
from hammett.core.screen import Screen

BOT_TEST_NAME = 'test'

CHAT_ID = 1

MESSAGE_ID = 1

PERMISSION_DENIED_STATE = '1'

PERMISSIONS_ORDER = []

USER_ID = 1


class BaseTestPermission(Permission, ABC):
    """The class implements a base permission for the tests."""

    def has_permission(self, _update, _context):
        """Append the method path to the permission order list."""
        PERMISSIONS_ORDER.append(f'{self.__class__.__name__}.{self.has_permission.__name__}')
        return True

    async def handle_permission_denied(self, _update, _context):
        """Represent a stub handler for the testing purposes."""
        return PERMISSION_DENIED_STATE


class BaseTestScreenWithDescription(Screen):
    """The class represents the base screen for the testing purposes."""

    description = 'Test description'


class BaseTestScreenWithHandler(Screen):
    """The class represents the base screen for the testing purposes."""

    @register_button_handler
    async def handler(self, _update, _context):
        """Represent a stub handler for the testing purposes."""
        return DEFAULT_STATE


class BaseTestScreenWithHideKeyboard(Screen):
    """The class represents the base screen for the testing purposes."""

    hide_keyboard = True


class BaseTestScreenWithMockedRenderer(Screen):
    """The class represents the base screen for the testing purposes."""

    def __init__(self):
        """Initialize a screen object."""
        super().__init__()
        self.renderer = TestRenderer(self.html_parse_mode)


class TestDenyingPermission(BaseTestPermission):
    """The class implements a permission that can never be given."""

    async def has_permission(self, _update, _context):
        """Represent a stub permission checker for the testing purpose."""
        return False


class TestGivingPermission(BaseTestPermission):
    """The class implements a permission that is always given."""

    async def has_permission(self, _update, _context):
        """Represent a stub permission checker for the testing purpose."""
        return True


class TestRenderer(Renderer):
    """The class implements screen rendering."""

    async def render(self, _update, _context, _config, **_kwargs):
        """Represent a stub for testing purposes."""
        return Message(
            MESSAGE_ID,
            datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
            Chat(CHAT_ID, ChatType.SENDER),
        )


class TestScreen(BaseTestScreenWithDescription):
    """The class implements a screen for the tests."""


class TestStartScreen(BaseTestScreenWithDescription, StartMixin):
    """The class implements a start screen for the tests."""


def get_bot(screens=None):
    """Return an initialized bot."""
    screens = [TestScreen] if screens is None else screens

    return Bot(
        BOT_TEST_NAME,
        entry_point=TestStartScreen,
        states={
            DEFAULT_STATE: screens,
        },
    )

"""The module contains the classes for the Hammett tests."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202

from abc import ABC

from hammett.core import Screen
from hammett.core.permissions import Permission
from hammett.core.screen import StartScreen

PERMISSION_DENIED_STATE = '1'

PERMISSIONS_ORDER = []


class BaseTestPermission(Permission, ABC):
    """The class implements a base permission for the tests."""

    def has_permission(self, _update, _context):
        """Appends the method path to the permission order list."""

        PERMISSIONS_ORDER.append(f'{self.__class__.__name__}.{self.has_permission.__name__}')
        return True

    async def handle_permission_denied(self, _update, _context):
        """A stub handler for the testing purposes."""

        return PERMISSION_DENIED_STATE


class TestDenyingPermission(BaseTestPermission):
    """The class implements a permission that can never be given."""

    async def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""

        return False


class TestGivingPermission(BaseTestPermission):
    """The class implements a permission that is always given."""

    async def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""

        return True


class TestScreen(Screen):
    """The class implements a screen for the tests."""

    description = 'A test description.'


class TestStartScreen(StartScreen):
    """The class implements a start screen for the tests."""

    description = 'A test StartScreen description.'

    async def start(self, _update, _context):
        """Invoked on the /start command."""

        return

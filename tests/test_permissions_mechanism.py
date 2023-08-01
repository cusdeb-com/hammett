"""The module contains the tests for the permissions mechanism. """

# ruff: noqa: ANN001, ANN101, ANN201, ANN202

from abc import ABC
from typing import TYPE_CHECKING, cast

from hammett.core.constants import DEFAULT_STAGE
from hammett.core.permissions import Permission
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase

if TYPE_CHECKING:
    from hammett.types import Handler, Stage

_PERMISSION_DENIED_STAGE = 1


class TestScreen(Screen):
    """The class implements a screen for the tests. """

    description = 'A test description.'


class BaseTestPermission(Permission, ABC):
    """The class implements a base permission for the tests. """

    async def handle_permission_denied(self, _update, _context):
        """A stub handler for the testing purposes. """

        return _PERMISSION_DENIED_STAGE


class TestDenyingPermission(BaseTestPermission):
    """The class implements a permission that can never be given. """

    async def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose. """

        return False


class TestGivingPermission(BaseTestPermission):
    """The class implements a permission that is always given. """

    async def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose. """

        return True


class TestPermissionWithSyncChecker(BaseTestPermission):
    """The class implements a permission where `has_permission` method is sync. """

    def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose. """

        return False


class PermissionsTests(BaseTestCase):
    """The class implements the tests for the permissions mechanism. """

    async def test_giving_permission(self):
        """Tests the case when the permission is giving. """

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestGivingPermission()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, DEFAULT_STAGE)

    async def test_denying_permission(self):
        """Tests the case when the permission is denied. """

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestDenyingPermission()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, _PERMISSION_DENIED_STAGE)

    async def test_sync_permission_denied(self):
        """Tests the case when the permission checker is a synchronous. """

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestPermissionWithSyncChecker()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, _PERMISSION_DENIED_STAGE)

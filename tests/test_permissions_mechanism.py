"""The module contains the tests for the permissions mechanism."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202, D401

from typing import TYPE_CHECKING, cast

from hammett.core.constants import DEFAULT_STATE
from hammett.core.permission import apply_permission_to
from hammett.test.base import BaseTestCase
from tests.base import (
    PERMISSION_DENIED_STATE,
    PERMISSIONS_ORDER,
    BaseTestPermission,
    TestDenyingPermission,
    TestGivingPermission,
    TestScreen,
)

if TYPE_CHECKING:
    from hammett.types import Handler, State


class TestPermissionWithSyncChecker(BaseTestPermission):
    """The class implements a permission where `has_permission` method is sync."""

    def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""
        return False


class MainPermission(BaseTestPermission):
    """The class implements a main permission that is always given."""


class SubPermission(BaseTestPermission):
    """The class implements a sub permission that is always given."""


class PermissionsTests(BaseTestCase):
    """The class implements the tests for the permissions mechanism."""

    async def test_execution_order_of_permissions(self):
        """Tests the scenario with multiple permission classes where
        strict execution order is required.
        """
        screen = TestScreen()
        wrapped_handler = apply_permission_to(screen.move)
        await wrapped_handler(self.update, self.context)
        expected = [
            'MainPermission.has_permission',
            'SubPermission.has_permission',
        ]
        self.assertEqual(PERMISSIONS_ORDER, expected)

    async def test_giving_permission(self):
        """Tests the case when the permission is giving."""
        screen = TestScreen()
        source = cast('Handler[..., State]', screen.move)

        permission_instance = TestGivingPermission()
        handler = permission_instance.check_permission(source)

        state = await handler(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    async def test_denying_permission(self):
        """Tests the case when the permission is denied."""
        screen = TestScreen()
        source = cast('Handler[..., State]', screen.move)

        permission_instance = TestDenyingPermission()
        handler = permission_instance.check_permission(source)

        state = await handler(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    async def test_sync_permission_denied(self):
        """Tests the case when the permission checker is a synchronous."""
        screen = TestScreen()
        source = cast('Handler[..., State]', screen.move)

        permission_instance = TestPermissionWithSyncChecker()
        handler = permission_instance.check_permission(source)

        state = await handler(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

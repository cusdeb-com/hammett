"""The module contains the tests for the permissions mechanism."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202

from typing import TYPE_CHECKING, cast

from hammett.core.constants import DEFAULT_STAGE
from hammett.test.base import BaseTestCase
from tests.base import (
    PERMISSION_DENIED_STAGE,
    BaseTestPermission,
    TestDenyingPermission,
    TestGivingPermission,
    TestScreen,
)

if TYPE_CHECKING:
    from hammett.types import Handler, Stage


class TestPermissionWithSyncChecker(BaseTestPermission):
    """The class implements a permission where `has_permission` method is sync."""

    def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""

        return False


class PermissionsTests(BaseTestCase):
    """The class implements the tests for the permissions mechanism."""

    async def test_giving_permission(self):
        """Tests the case when the permission is giving."""

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestGivingPermission()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, DEFAULT_STAGE)

    async def test_denying_permission(self):
        """Tests the case when the permission is denied."""

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestDenyingPermission()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, PERMISSION_DENIED_STAGE)

    async def test_sync_permission_denied(self):
        """Tests the case when the permission checker is a synchronous."""

        screen = TestScreen()
        source = cast('Handler[..., Stage]', screen.goto)

        permission_instance = TestPermissionWithSyncChecker()
        handler = permission_instance.check_permission(source)

        stage = await handler(self.update, self.context)
        self.assertEqual(stage, PERMISSION_DENIED_STAGE)

"""The module contains the tests for the permissions mechanism.

In the case of testing the permission mechanism, it is necessary to create
a new Screen class in each test case. This is because the Screen object is
a singleton, and when wrapping all its handlers, they share their state between
the tests, leading to unstable behavior.
"""

# ruff: noqa: S106

from hammett.core.constants import DEFAULT_STATE
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.permission import Permission, ignore_permissions
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import (
    PERMISSION_DENIED_STATE,
    PERMISSIONS_ORDER,
    BaseTestPermission,
    BaseTestScreenWithDescription,
    BaseTestScreenWithHandler,
    TestDenyingPermission,
    get_bot,
)


class MainPermission(BaseTestPermission):
    """The class implements a main permission that is always given."""


class PermissionWithoutHandlePermissionDeniedMethod(Permission):
    """The class represents a permission that does not implement
    the mandatory method `handle_permission_denied`.
    """

    def has_permission(self, _update, _context):
        """Represent a stub permission checker for the testing purposes."""
        return False


class PermissionWithoutHasPermissionMethod(Permission):
    """The class represents a permission that does not implement
    the mandatory method `has_permission`.
    """

    async def handle_permission_denied(self, _update, _context):
        """Represent a stub handler for the testing purposes."""
        return PERMISSION_DENIED_STATE


class SubPermission(BaseTestPermission):
    """The class implements a sub permission that is always given."""


class TestPermissionWithSyncChecker(BaseTestPermission):
    """The class implements a permission where `has_permission` method is sync."""

    def has_permission(self, _update, _context):
        """Represent a stub permission checker for the testing purpose."""
        return False


class PermissionsTests(BaseTestCase):
    """The class implements the tests for the permissions mechanism."""

    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_denying_permission(self):
        """Test the case when the permission is denied."""

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        state = await screen.move(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.MainPermission',
        'tests.test_permissions_mechanism.SubPermission',
    ], TOKEN='secret-token')
    async def test_execution_order_of_permissions(self):
        """Test the scenario with multiple permission classes where
        strict execution order is required.
        """

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        await screen.move(self.update, self.context)
        expected = [
            'MainPermission.has_permission',
            'SubPermission.has_permission',
        ]
        self.assertEqual(PERMISSIONS_ORDER, expected)

    @override_settings(PERMISSIONS=['tests.base.TestGivingPermission'], TOKEN='secret-token')
    async def test_giving_permission(self):
        """Test the case when the permission is giving."""

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        state = await screen.move(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.PermissionWithoutHandlePermissionDeniedMethod',
    ], TOKEN='secret-token')
    async def test_handle_permission_denied_method_is_not_implemented(self):
        """Test the case when the handle_permission_denied method is not implemented."""

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        with self.assertRaises(NotImplementedError):
            await screen.move(self.update, self.context)

    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.PermissionWithoutHasPermissionMethod',
    ], TOKEN='secret-token')
    async def test_has_permission_method_is_not_implemented(self):
        """Test the case when the has_permission method is not implemented."""

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        with self.assertRaises(NotImplementedError):
            await screen.move(self.update, self.context)

    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_ignoring_one_permission(self):
        """Test the case when one permission is ignored."""

        class ScreenWithIgnorePermissionHandler(BaseTestScreenWithDescription):
            """The class implements a screen with a handler that ignores
            the TestDenyingPermission permission.
            """

            @ignore_permissions([TestDenyingPermission])
            @register_button_handler
            async def handler(self, _update, _context):
                """Represent a handler which ignores TestDenyingPermission permission."""
                return DEFAULT_STATE

        get_bot([ScreenWithIgnorePermissionHandler])
        screen = ScreenWithIgnorePermissionHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @override_settings(PERMISSIONS=[
        'tests.base.TestGivingPermission',
        'tests.base.TestDenyingPermission',
    ], TOKEN='secret-token')
    async def test_ignoring_second_permission(self):
        """Test the case when the second permission is ignored."""

        class ScreenWithIgnorePermissionHandler(BaseTestScreenWithDescription):
            """The class implements a screen with a handler that ignores
            the TestDenyingPermission permission.
            """

            @ignore_permissions([TestDenyingPermission])
            @register_button_handler
            async def handler(self, _update, _context):
                """Represent a handler which ignores TestDenyingPermission permission."""
                return DEFAULT_STATE

        get_bot([ScreenWithIgnorePermissionHandler])
        screen = ScreenWithIgnorePermissionHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.TestPermissionWithSyncChecker',
    ], TOKEN='secret-token')
    async def test_sync_permission_denied(self):
        """Test the case when the permission checker is a synchronous."""

        class TestScreen(BaseTestScreenWithDescription):
            """The class implements a screen for this test."""

        get_bot([TestScreen])
        screen = TestScreen()

        state = await screen.move(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_wrapping_handler_with_permission_specified(self):
        """Test the case when a handler is wrapped with a permission."""

        class ScreenWithHandler(BaseTestScreenWithDescription, BaseTestScreenWithHandler):
            """The class implements a screen with a handler."""

        get_bot([ScreenWithHandler])
        screen = ScreenWithHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_wrapping_start_method_with_permission_specified(self):
        """Test the case when the start method is wrapped with a permission."""

        class TestStartScreen(BaseTestScreenWithDescription, StartMixin):
            """The class implements a start screen for this test."""

        get_bot([TestStartScreen])
        screen = TestStartScreen()

        state = await screen.start(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

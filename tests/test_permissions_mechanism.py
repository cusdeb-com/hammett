"""The module contains the tests for the permissions mechanism."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202, ANN205, S106, SLF001

import pytest

from hammett.core import Application, Screen
from hammett.core.constants import DEFAULT_STATE
from hammett.core.handlers import register_button_handler
from hammett.core.permissions import Permission, ignore_permissions
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import (
    PERMISSION_DENIED_STATE,
    PERMISSIONS_ORDER,
    BaseTestPermission,
    TestDenyingPermission,
    TestScreen,
    TestStartScreen,
)
from tests.test_application import _APPLICATION_TEST_NAME


class TestPermissionWithSyncChecker(BaseTestPermission):
    """The class implements a permission where `has_permission` method is sync."""

    def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""

        return False


class MainPermission(BaseTestPermission):
    """The class implements a main permission that is always given."""


class NotImplementHasPermissionMethodPermission(Permission):
    """The class does not implement required has_permission method."""

    async def handle_permission_denied(self, _update, _context):
        """A stub handler for the testing purposes."""

        return PERMISSION_DENIED_STATE


class ScreenWithIgnorePermissionHandler(Screen):
    """The class implements screen which ignores TestDenyingPermission permission."""

    description = 'Test description'

    @ignore_permissions([TestDenyingPermission])
    @register_button_handler
    async def handler(self, _update, _context):
        """Handler which ignores TestDenyingPermission permission."""

        return DEFAULT_STATE


class ScreenWithHandler(Screen):
    """The class implements screen with handler."""

    description = 'Test description'

    @register_button_handler
    async def handler(self, _update, _context):
        """A stub handler for the testing purposes."""

        return DEFAULT_STATE


class NotImplementPermissionDeniedMethodPermission(Permission):
    """The class does not implement required handle_permission_denied method."""

    def has_permission(self, _update, _context):
        """A stub permission checker for the testing purpose."""

        return False


class SubPermission(BaseTestPermission):
    """The class implements a sub permission that is always given."""


class PermissionsTests(BaseTestCase):
    """The class implements the tests for the permissions mechanism."""

    @staticmethod
    def _init_application(screens=None):
        """Returns an initialized application."""

        Application(
            _APPLICATION_TEST_NAME,
            entry_point=TestStartScreen,
            states={
                DEFAULT_STATE: screens,
            },
        )

    @pytest.mark.xdist_group('test_wrapping_handler_with_permissions_specified')
    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_wrapping_handler_with_permissions_specified(self):
        """Tests the case when handler is wrapped with permissions."""

        self._init_application([ScreenWithHandler])
        screen = ScreenWithHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @pytest.mark.xdist_group('test_wrapping_start_method_with_permissions_specified')
    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_wrapping_start_method_with_permissions_specified(self):
        """Tests the case when the start method is wrapped with permissions."""

        self._init_application([TestStartScreen])
        screen = TestStartScreen()

        state = await screen.start(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @pytest.mark.xdist_group('test_execution_order_of_permissions')
    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.MainPermission',
        'tests.test_permissions_mechanism.SubPermission',
    ], TOKEN='secret-token')
    async def test_execution_order_of_permissions(self):
        """Tests the scenario with multiple permission classes where
        strict execution order is required.
        """

        self._init_application([TestScreen])
        screen = TestScreen()

        await screen.goto(self.update, self.context)
        expected = [
            'MainPermission.has_permission',
            'SubPermission.has_permission',
        ]
        self.assertEqual(PERMISSIONS_ORDER, expected)

    @pytest.mark.xdist_group('test_giving_permission')
    @override_settings(PERMISSIONS=['tests.base.TestGivingPermission'], TOKEN='secret-token')
    async def test_giving_permission(self):
        """Tests the case when the permission is giving."""

        self._init_application([TestScreen])
        screen = TestScreen()

        state = await screen.goto(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @pytest.mark.xdist_group('test_denying_permission')
    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_denying_permission(self):
        """Tests the case when the permission is denied."""

        self._init_application([TestScreen])
        screen = TestScreen()

        state = await screen.goto(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @pytest.mark.xdist_group('test_sync_permission_denied')
    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.TestPermissionWithSyncChecker',
    ], TOKEN='secret-token')
    async def test_sync_permission_denied(self):
        """Tests the case when the permission checker is a synchronous."""

        self._init_application([TestScreen])
        screen = TestScreen()

        state = await screen.goto(self.update, self.context)
        self.assertEqual(state, PERMISSION_DENIED_STATE)

    @pytest.mark.xdist_group('test_ignore_one_permission')
    @override_settings(PERMISSIONS=['tests.base.TestDenyingPermission'], TOKEN='secret-token')
    async def test_ignore_one_permission(self):
        """Tests the case when one permission is ignored."""

        self._init_application([ScreenWithIgnorePermissionHandler])
        screen = ScreenWithIgnorePermissionHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @pytest.mark.xdist_group('test_ignore_second_permission')
    @override_settings(PERMISSIONS=[
        'tests.base.TestGivingPermission',
        'tests.base.TestDenyingPermission',
    ], TOKEN='secret-token')
    async def test_ignore_second_permission(self):
        """Tests the case when second permission is ignored."""

        self._init_application([ScreenWithIgnorePermissionHandler])
        screen = ScreenWithIgnorePermissionHandler()

        state = await screen.handler(self.update, self.context)
        self.assertEqual(state, DEFAULT_STATE)

    @pytest.mark.xdist_group('test_has_permission_is_not_implement')
    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.NotImplementHasPermissionMethodPermission',
    ], TOKEN='secret-token')
    async def test_has_permission_is_not_implement(self):
        """Tests the case when the has_permission method is not implement."""

        self._init_application([TestScreen])
        screen = TestScreen()

        with self.assertRaises(NotImplementedError):
            await screen.goto(self.update, self.context)

    @pytest.mark.xdist_group('test_handle_permission_denied_is_not_implement')
    @override_settings(PERMISSIONS=[
        'tests.test_permissions_mechanism.NotImplementPermissionDeniedMethodPermission',
    ], TOKEN='secret-token')
    async def test_handle_permission_denied_is_not_implement(self):
        """Tests the case when the handle_permission_denied method is not implement."""

        self._init_application([TestScreen])
        screen = TestScreen()

        with self.assertRaises(NotImplementedError):
            await screen.goto(self.update, self.context)

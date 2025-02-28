"""The module contains the tests for the hiders mechanism."""

from hammett.conf import settings
from hammett.core.button import Button
from hammett.core.constants import SourceTypes
from hammett.core.exceptions import HiderIsUnregistered, ImproperlyConfigured
from hammett.core.hider import (
    ONLY_FOR_ADMIN,
    ONLY_FOR_BETA_TESTERS,
    ONLY_FOR_MODERATORS,
    Hider,
    HidersChecker,
)
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings

_TEST_BUTTON_NAME = 'Test button'

_TEST_URL = 'https://github.com/cusdeb-com/hammett'

_ONLY_FOR_DEVELOPERS = 10


class TestHidersChecker(HidersChecker):
    """The class implements a hiders checker for the tests."""

    def is_admin(self, _update, _context):
        """Represent a stub hiders checker for the testing purposes."""
        return settings.IS_ADMIN

    def is_moderator(self, _update, _context):
        """Represent a stub hiders checker for the testing purposes."""
        return settings.IS_MODERATOR


class TestAsyncHidersChecker(HidersChecker):
    """The class implements an asynchronous hiders checker
    for the tests.
    """

    async def is_admin(self, _update, _context):
        """Represent a stub hiders checker for the testing purposes."""
        return settings.IS_ADMIN

    async def is_moderator(self, _update, _context):
        """Represent a stub hiders checker for the testing purposes."""
        return settings.IS_MODERATOR


class HidersCheckerTests(BaseTestCase):
    """The class implements the tests for the hiders checker mechanism."""

    async def _test_hider(self):
        """Implement a method with common logic shared by some tests here."""
        settings.IS_ADMIN = True
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertTrue(visibility)

        settings.IS_ADMIN = False
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertFalse(visibility)

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestAsyncHidersChecker')
    async def test_async_hider(self):
        """Test the case when an asynchronous hider is used to control
        a button visibility.
        """
        await self._test_hider()

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker')
    async def test_creating_button_with_unregistered_hider(self):
        """Test creating a button with an unregistered hider."""
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(_ONLY_FOR_DEVELOPERS),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        with self.assertRaises(HiderIsUnregistered):
            await button.create(self.update, self.context)

    def test_empty_setting(self):
        """Test the case when a button uses the hiders mechanism,
        but the 'HIDERS_CHECKER' setting is empty.
        """
        with self.assertRaises(ImproperlyConfigured):
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker')
    async def test_hider(self):
        """Test the case when a hider is used to control
        a button visibility.
        """
        await self._test_hider()

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker')
    async def test_hiders_chain(self):
        """Test the case when hiders are combined using the OR operator."""
        settings.IS_ADMIN = False
        settings.IS_MODERATOR = True
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN) | Hider(ONLY_FOR_MODERATORS),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertTrue(visibility)

        settings.IS_ADMIN = False
        settings.IS_MODERATOR = False
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN) | Hider(ONLY_FOR_MODERATORS),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertFalse(visibility)

    @override_settings(HIDERS_CHECKER='test')
    def test_invalid_import(self):
        """Test the case when the 'HIDERS_CHECKER' contains
        an invalid module path.
        """
        with self.assertRaises(ImportError):
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )

    @override_settings(HIDERS_CHECKER='test.TestHidersChecker')
    def test_invalid_importing_hider_checker_path(self):
        """Test the case when the 'HIDERS_CHECKER' contains
        an invalid HiderChecker class path.
        """
        with self.assertRaises(ImportError):
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourceTypes.URL_SOURCE_TYPE,
            )

    @override_settings(HIDERS_CHECKER='hammett.core.hider.HidersChecker')
    async def test_visibility_of_button_using_default_hider_checker(self):
        """Test a visibility of a button using the default 'HidersChecker'."""
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN) |
            Hider(ONLY_FOR_BETA_TESTERS) |
            Hider(ONLY_FOR_MODERATORS),
            source_type=SourceTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertFalse(visibility)

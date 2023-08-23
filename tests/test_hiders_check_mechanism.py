"""The module contains the tests for the hiders mechanism."""

# ruff: noqa: ANN001, ANN101, ANN201, ANN202

from hammett.conf import settings
from hammett.core.constants import SourcesTypes
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.hiders import (
    ONLY_FOR_ADMIN,
    ONLY_FOR_MODERATORS,
    Hider,
    HidersChecker,
)
from hammett.core.screen import Button
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings

_TEST_BUTTON_NAME = 'Test button'

_TEST_URL = 'https://github.com/cusdeb-com/hammett'


class TestHidersChecker(HidersChecker):
    """The class implements a hiders checker for the tests."""

    def is_admin(self, _update, _context):
        """A stub hiders checker for the testing purposes."""

        return settings.IS_ADMIN

    def is_moderator(self, _update, _context):
        """A stub hiders checker for the testing purposes."""

        return settings.IS_MODERATOR


class TestAsyncHidersChecker(HidersChecker):
    """The class implements an asynchronous hiders checker
    for the tests.
    """

    async def is_admin(self, _update, _context):
        """A stub hiders checker for the testing purposes."""

        return settings.IS_ADMIN

    async def is_moderator(self, _update, _context):
        """A stub hiders checker for the testing purposes."""

        return settings.IS_MODERATOR


class HidersCheckerTests(BaseTestCase):
    """The class implements the tests for the hiders checker mechanism."""

    async def _test_hider(self):
        """The method is intended to be invoked by other tests that use
        different hiders checkers.
        """

        settings.IS_ADMIN = True
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN),
            source_type=SourcesTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertTrue(visibility)

        settings.IS_ADMIN = False
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN),
            source_type=SourcesTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertFalse(visibility)

    def test_empty_setting(self):
        """Tests the case when a button uses the hiders mechanism,
        but the 'HIDERS_CHECKER' setting is empty.
        """

        with self.assertRaises(ImproperlyConfigured):
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourcesTypes.URL_SOURCE_TYPE,
            )

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestAsyncHidersChecker')
    async def test_async_hider(self):
        """Test the case when an asynchronous hider is used to control
        a button visibility.
        """

        await self._test_hider()

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker')
    async def test_hider(self):
        """Test the case when a hider is used to control
        a button visibility.
        """

        await self._test_hider()

    @override_settings(HIDERS_CHECKER='tests.test_hiders_check_mechanism.TestHidersChecker')
    async def test_hiders_chain(self):
        """Tests the case when hiders are combined using the OR operator."""

        settings.IS_ADMIN = False
        settings.IS_MODERATOR = True
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN) | Hider(ONLY_FOR_MODERATORS),
            source_type=SourcesTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertTrue(visibility)

        settings.IS_ADMIN = False
        settings.IS_MODERATOR = False
        button = Button(
            _TEST_BUTTON_NAME,
            _TEST_URL,
            hiders=Hider(ONLY_FOR_ADMIN) | Hider(ONLY_FOR_MODERATORS),
            source_type=SourcesTypes.URL_SOURCE_TYPE,
        )
        _, visibility = await button.create(self.update, self.context)
        self.assertFalse(visibility)

    @override_settings(HIDERS_CHECKER='test')
    def test_invalid_import(self):
        """Tests the case when the 'HIDERS_CHECKER' contains
        an invalid module path.
        """

        with self.assertRaises(ImportError):
            Button(
                _TEST_BUTTON_NAME,
                _TEST_URL,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourcesTypes.URL_SOURCE_TYPE,
            )

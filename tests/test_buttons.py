"""The module contains the tests for buttons."""

# ruff: noqa: ANN101, ANN201

from hammett.core.constants import SourcesTypes
from hammett.core.exceptions import UnknownSourceType
from hammett.core.screen import Button
from hammett.test.base import BaseTestCase
from tests.base import TestScreen

_TEST_PAYLOAD = 'test payload'

_UNKNOWN_SOURCE_TYPE = 100


class AnythingElseButScreen:
    """A dummy class used for the testing purposes."""


class ButtonsTests(BaseTestCase):
    """The class implements the tests for buttons."""

    async def test_non_callable_source_as_handler(self):
        """Tests the case when a button handler is not callable."""

        with self.assertRaises(TypeError):
            Button(
                'Test',
                None,  # is not callable, so it's invalid
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            )

    async def test_unknown_source_type(self):
        """Tests the case when an unknown source type passed."""

        with self.assertRaises(UnknownSourceType):
            button = Button(
                'Test',
                TestScreen,
                source_type=_UNKNOWN_SOURCE_TYPE,
            )
            await button.create(self.update, self.context)

    async def test_using_random_class_instead_of_screen_for_goto(self):
        """
        Tests the case when the source type is `GOTO_SOURCE_TYPE` but
        the source isn't a subclass of Screen.
        """

        with self.assertRaises(TypeError):
            Button(
                'Test',
                AnythingElseButScreen,  # is not a subclass of Screen, so it's invalid
                source_type=SourcesTypes.GOTO_SOURCE_TYPE,
            )

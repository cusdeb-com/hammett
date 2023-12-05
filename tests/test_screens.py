"""The module contains the tests for screens."""

# ruff: noqa: ANN101, ANN201

from hammett.core import Screen
from hammett.core.exceptions import ScreenDescriptionIsEmpty
from hammett.core.screen import StartScreen
from hammett.test.base import BaseTestCase


class TestScreenWithoutDescription(Screen):
    """The class implements a screen without description."""


class StartScreenWithoutStartMethod(StartScreen):
    """The class implements a start screen without start method."""

    description = 'A test description.'


class ScreenTests(BaseTestCase):
    """The class implements the tests for the screens."""

    async def test_screen_without_description(self):
        """Tests the case when the description is empty."""

        screen = TestScreenWithoutDescription()
        with self.assertRaises(ScreenDescriptionIsEmpty):
            await screen.goto(self.update, self.context)

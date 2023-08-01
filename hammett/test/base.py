"""The module contains the base class for the tests for
both Hammett itself and the bots based on the framework.
"""

import asyncio
import unittest
from typing import TYPE_CHECKING

from asgiref.sync import async_to_sync
from telegram import Update
from telegram.ext import Application, CallbackContext

if TYPE_CHECKING:
    from typing_extensions import Self


class BaseTestCase(unittest.TestCase):
    """The class that subclasses unittest.TestCase to make it
    familiar with the specifics of the framework.
    """

    update: 'Update'
    context: 'CallbackContext'  # type: ignore[type-arg]

    def __init__(self: 'Self', method_name: str) -> None:
        self.context: 'CallbackContext' = CallbackContext(  # type: ignore[type-arg]
            Application.builder(),  # type: ignore[arg-type]
        )
        self.update = Update(1)

        super().__init__(method_name)

    def __call__(self: 'Self', result: 'unittest.result.TestResult | None' = None) -> None:
        """Overrides __call__ to wrap asynchronous tests. """

        test_method = getattr(self, self._testMethodName)
        if asyncio.iscoroutinefunction(test_method):
            setattr(self, self._testMethodName, async_to_sync(test_method))

        super().__call__(result)

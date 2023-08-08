# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
        """Overrides __call__ to wrap asynchronous tests."""

        test_method = getattr(self, self._testMethodName)
        if asyncio.iscoroutinefunction(test_method):
            setattr(self, self._testMethodName, async_to_sync(test_method))

        super().__call__(result)

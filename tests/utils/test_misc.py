"""The module contains tests for the miscellaneous helpers."""

from unittest.mock import AsyncMock

from telegram import Update

from hammett.test.base import BaseTestCase
from hammett.utils.misc import get_callback_query


class UtilsMiscTests(BaseTestCase):
    """The class implements the tests for the miscellaneous helpers."""

    _mock_query = AsyncMock()

    def get_update(self) -> 'Update':
        """Return the `Update` object for testing purposes."""
        return Update(self.update_id, message=self.message, callback_query=self._mock_query)

    async def test_get_callback_query_answers_and_returns_query(self):
        """Test the case when get_callback_query answers and returns query."""
        actual = await get_callback_query(self.update)

        self._mock_query.answer.assert_awaited_once()
        self.assertIs(actual, self._mock_query)

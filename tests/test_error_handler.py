"""The module contains the tests for the error handler."""

from telegram.error import BadRequest, TimedOut

from hammett.error_handler import default_error_handler
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings


class ErrorHandlerTests(BaseTestCase):
    """The class implements the tests for the default error handler."""

    async def test_error_is_raised_when_not_ignored(self):
        """Test the case when errors are not ignored and thus raised."""
        self.context.error = TimedOut(message='Timed out')

        with self.assertRaises(TimedOut):
            await default_error_handler(self.update, self.context)

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_TIMED_OUT': True})
    async def test_non_matching_error_is_raised_even_if_some_flags_set(self):
        """Test unrelated errors are not swallowed by ignore flags and are raised."""
        class CustomError(Exception):
            pass

        self.context.error = CustomError('boom')

        with self.assertRaises(CustomError):
            await default_error_handler(self.update, self.context)

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_QUERY_IS_TOO_OLD': True})
    async def test_warning_logged_for_query_too_old_when_ignored(self):
        """Test the case when BadRequest(Query is too old) is ignored and logged."""
        self.context.error = BadRequest(message=(
            'Query is too old and response timeout expired or query id is invalid'
        ))

        with self.assertLogs('hammett.error_handler', level='WARNING') as log:
            await default_error_handler(self.update, self.context)

        self.assertEqual(len(log.records), 1)
        self.assertIn('Query is too old', log.records[0].message)

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_UPDATE_MASSAGE_FAIL': True})
    async def test_warning_logged_for_message_not_modified_when_ignored(self):
        """Test the case when BadRequest(Message is not modified) is ignored and logged."""
        self.context.error = BadRequest(message='Message is not modified: text is the same')

        with self.assertLogs('hammett.error_handler', level='WARNING') as log:
            await default_error_handler(self.update, self.context)

        self.assertEqual(len(log.records), 1)
        self.assertIn('Message is not modified', log.records[0].message)

    @override_settings(ERROR_HANDLER_CONF={'IGNORE_TIMED_OUT': True})
    async def test_warning_logged_for_timed_out_when_ignored(self):
        """Test the case when TimedOut is ignored and logged as warning."""
        self.context.error = TimedOut(message='Timed out')

        with self.assertLogs('hammett.error_handler', level='WARNING') as log:
            await default_error_handler(self.update, self.context)

        self.assertEqual(len(log.records), 1)
        self.assertIn('Timed out', log.records[0].message)

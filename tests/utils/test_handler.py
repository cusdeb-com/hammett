"""The module contains tests for the handler helpers."""

from hammett.test.base import BaseTestCase
from hammett.utils.handler import wraps_handler


class UtilsHandlerTests(BaseTestCase):
    """The class implements tests for the handler helpers."""

    def test_wraps_handler_preserves_assigned_attributes(self):
        """Test preserving wrapper assignments from the wrapped handler."""

        class TestScreen:
            """The class implements a test screen for testing purposes."""

            def handler(self):
                """Represent a stub handler for the testing purposes."""
                return 'original'

        def wrapper_handler():
            """Represent a wrapper handler for the testing purposes."""
            return 'wrapper'

        screen = TestScreen()
        handler = screen.handler
        wrapped_handler = wraps_handler(handler)(wrapper_handler)

        self.assertIs(wrapped_handler, wrapper_handler)
        self.assertIs(wrapped_handler.__wrapped__, handler)
        self.assertIs(wrapped_handler.__self__, screen)
        self.assertEqual(wrapped_handler.__name__, handler.__name__)
        self.assertEqual(wrapped_handler.__qualname__, handler.__qualname__)
        self.assertEqual(wrapped_handler.__module__, handler.__module__)
        self.assertEqual(wrapped_handler.__doc__, handler.__doc__)

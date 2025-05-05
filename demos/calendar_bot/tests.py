"""The module contains the tests for HammettCalendarBot."""

import os
import unittest

from hammett.test.base import BaseTestCase


class HammettCalendarBotTests(BaseTestCase):
    """The class contains the tests for HammettCalendarBot."""


if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('TOKEN', 'test-token')

    unittest.main()

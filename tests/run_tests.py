"""The module runs all the tests."""

# ruff: noqa: F401

import os
import unittest

from tests.test_application import ApplicationTests
from tests.test_buttons import ButtonsTests
from tests.test_hiders_check_mechanism import HidersCheckerTests
from tests.test_permissions_mechanism import PermissionsTests
from tests.test_screens import ScreenTests

if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'tests.settings')

    unittest.main()

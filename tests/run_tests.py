"""The module runs all the tests. """

import os
import unittest

from tests.test_hiders_check_mechanism import HidersCheckerTests

if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'tests.settings')

    unittest.main()

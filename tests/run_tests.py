"""The module runs all the tests."""

# ruff: noqa: F401

import os
import unittest

from tests.test_bot import BotTests
from tests.test_buttons import ButtonsTests
from tests.test_handers_render import HandlersRenderTests
from tests.test_handlers import HandlersTests
from tests.test_hiders_check_mechanism import HidersCheckerTests
from tests.test_mixins import MixinTests
from tests.test_permissions_mechanism import PermissionsTests
from tests.test_persistence import PersistenceTests
from tests.test_screens import ScreenTests
from tests.test_start_marker import StartMarkerTests
from tests.test_widgets.test_carousel import CarouselWidgetTests

if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'tests.settings')

    unittest.main()

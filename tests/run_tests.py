"""The module runs all the tests."""

# ruff: noqa: F401

import os
import unittest

from tests.test_bot import BotTests
from tests.test_buttons import ButtonsTests
from tests.test_conf import ConfigurationTests
from tests.test_error_handler import ErrorHandlerTests
from tests.test_handers_render import HandlersRenderTests
from tests.test_handlers import HandlersTests
from tests.test_hiders_check_mechanism import HidersCheckerTests
from tests.test_mixins import (
    I18NMixinTests,
    I18NMixinTestsWithoutUpdate,
    RouteMixinTests,
    StartMixinTests,
)
from tests.test_permissions_mechanism import PermissionsTests
from tests.test_persistence import PersistenceTests
from tests.test_renderer import RendererTests
from tests.test_screens import ScreenTests, ScreenTestsWithoutUpdate
from tests.test_start_marker import StartMarkerTests
from tests.test_template import TemplateTests
from tests.utils.test_misc import UtilsMiscTests
from tests.utils.test_module_loading import UtilsModuleLoadingTests
from tests.utils.test_render_config import (
    UtilsRenderConfigTests,
    UtilsRenderConfigTestsWithoutUpdate,
)
from tests.utils.test_translation import (
    UtilsTranslationCatalogTests,
    UtilsTranslationTests,
)
from tests.widgets.test_base import (
    BaseChoiceWidgetTests,
    BaseStateWidgetTests,
    BaseStateWidgetTestsWithoutUpdate,
    BaseWidgetTests,
)
from tests.widgets.test_calendar import CalendarWidgetTests
from tests.widgets.test_carousel import CarouselWidgetTests, CarouselWidgetWithoutUpdateTests
from tests.widgets.test_multi_choice import (
    BaseChoiceWidgetTestsUsingMultiChoiceWidget,
    BaseStateWidgetTestsUsingMultiChoiceWidget,
    BaseStateWidgetTestsUsingMultiChoiceWidgetWithoutUpdate,
    MultiChoiceWidgetTests,
)
from tests.widgets.test_single_choice import (
    BaseChoiceWidgetTestsUsingSingleChoiceWidget,
    SingleChoiceWidgetTests,
)

if __name__ == '__main__':
    os.environ.setdefault('HAMMETT_SETTINGS_MODULE', 'tests.settings')

    unittest.main()

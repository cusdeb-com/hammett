"""The module contains the tests for the mixins."""

from unittest.mock import AsyncMock, MagicMock

from hammett.core.constants import DEFAULT_STATE, RenderConfig
from hammett.core.exceptions import ImproperlyConfigured, ScreenRouteIsEmpty
from hammett.core.mixins import I18NMixin, RouteMixin
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import TEST_STATE, TestStartScreen


class TestI18NScreen(I18NMixin):
    """The class implements a screen with I18N support for the tests."""


class TestRouteScreen(RouteMixin):
    """The class implements a route screen for the tests."""

    routes = (({DEFAULT_STATE}, TEST_STATE),)


class TestRouteScreenWithoutRoutes(RouteMixin):
    """The class implements a screen without specified routes attribute."""


class I18NMixinTests(BaseTestCase):
    """The class implements the tests for the I18NMixin."""

    @override_settings(LANGUAGE_CODE='en')
    async def test_default_language_code_getting(self):
        """Test the case when the logic of getting a language code is overridden."""
        screen = TestI18NScreen()
        self.context.user_data.clear()
        self.context.user_data.update({'language_code': 'ru'})

        language = await screen.get_language_code(None, self.context)
        self.assertEqual(language, 'ru')

    @override_settings(LANGUAGE_CODE='de')
    async def test_language_code_getting_when_user_data_is_empty(self):
        """Test the case when a language code is taken from settings if user_data is empty."""
        screen = TestI18NScreen()
        self.context.user_data.clear()

        language = await screen.get_language_code(None, self.context)
        self.assertEqual(language, 'de')

    async def test_set_language_code_is_noop_when_user_data_is_empty(self):
        """Test the case when set_language_code does nothing for empty user_data."""
        screen = TestI18NScreen()
        self.context.user_data.clear()

        await screen.set_language_code(None, self.context, 'it')
        self.assertNotIn('language_code', self.context.user_data)

    async def test_set_language_code_updates_user_data_when_present(self):
        """Test the case when set_language_code updates non-empty user_data."""
        screen = TestI18NScreen()
        self.context.user_data.clear()
        self.context.user_data.update({'dummy': True})

        language_code = 'es'
        await screen.set_language_code(None, self.context, language_code)
        self.assertIn('language_code', self.context.user_data)
        self.assertEqual(self.context.user_data['language_code'], language_code)


class RouteMixinTests(BaseTestCase):
    """The class implements the tests for RouteMixin."""

    async def test_get_return_state_from_routes_when_match(self):
        """Test the case when the current state matches a route."""
        screen = TestRouteScreen()
        screen.get_current_state = MagicMock(return_value=DEFAULT_STATE)

        result_state = screen.get_return_state_from_routes(self.context)
        self.assertEqual(result_state, TEST_STATE)

    async def test_get_return_state_from_routes_when_no_match(self):
        """Test the case when the current state does not match any route."""
        screen = TestRouteScreen()
        screen.get_current_state = MagicMock(return_value=TEST_STATE)

        result_state = screen.get_return_state_from_routes(self.context)
        self.assertEqual(result_state, TEST_STATE)

    async def test_jump_along_route_sets_as_new_message_and_renders(self):
        """Test the case when jump_along_route sets as_new_message and renders."""
        screen = TestRouteScreen()
        screen.get_current_state = MagicMock(return_value=DEFAULT_STATE)
        screen.get_config = AsyncMock(return_value=RenderConfig())
        screen.render = AsyncMock()

        state = await screen.jump_along_route(self.update, self.context)

        screen.get_config.assert_awaited_once()
        screen.render.assert_awaited_once()

        called_kwargs = screen.render.call_args.kwargs
        self.assertIn('config', called_kwargs)
        self.assertTrue(called_kwargs['config'].as_new_message)
        self.assertEqual(state, TEST_STATE)

    def test_invalid_routes_structure_raises_exception(self):
        """Test the case when the routes attribute has an invalid structure."""

        class BadRoutesScreen(RouteMixin):
            routes = ({DEFAULT_STATE}, TEST_STATE)

        with self.assertRaises(ImproperlyConfigured):
            BadRoutesScreen()

    async def test_move_along_route_renders_without_as_new_message(self):
        """Test the case when move_along_route renders without changing message."""
        screen = TestRouteScreen()
        screen.get_current_state = MagicMock(return_value=DEFAULT_STATE)
        screen.get_config = AsyncMock(return_value=RenderConfig())
        screen.render = AsyncMock()

        state = await screen.move_along_route(self.update, self.context)

        screen.get_config.assert_awaited_once()
        screen.render.assert_awaited_once()

        called_kwargs = screen.render.call_args.kwargs
        self.assertIn('config', called_kwargs)
        self.assertFalse(called_kwargs['config'].as_new_message)
        self.assertEqual(state, TEST_STATE)

    async def test_route_mixin_raises_exception_when_routes_attribute_is_empty(self):
        """Test that ScreenRouteIsEmpty is raised when routes attribute is missing or empty."""
        with self.assertRaises(ScreenRouteIsEmpty):
            TestRouteScreenWithoutRoutes()


class StartMixinTests(BaseTestCase):
    """The class implements the tests for StartMixin."""

    async def test_start_handler_of_start_mixin(self):
        """Test the case when the start method from StartMixin is used."""
        screen = TestStartScreen()
        state = await screen.start(self.update, self.context)

        self.assertEqual(DEFAULT_STATE, state)

"""The module implements the tests for the configuration module."""

# ruff: noqa: SLF001

import os
from types import SimpleNamespace
from unittest.mock import patch

from hammett.conf import GlobalSettings, global_settings
from hammett.conf.lazy_settings import LazyObject, LazySettings, Settings
from hammett.core.exceptions import ImproperlyConfiguredError
from hammett.test.base import BaseTestCase


class ConfigurationTests(BaseTestCase):
    """The class implements the tests for the configuration module."""

    def __init__(self, method_name: str) -> None:
        """Initialize a base test case object."""
        super(BaseTestCase, self).__init__(method_name)

    def test_global_settings_delegates_getattr_and_repr(self):
        """Test that GlobalSettings delegates getattr and repr to global_settings."""
        settings = GlobalSettings()

        assert settings.DOMAIN == global_settings.DOMAIN
        assert repr(settings) == f'<{settings.__class__.__name__}>'

    def test_lazy_object_delattr_raises_on_wrapped(self):
        """Test LazyObject.__delattr__ raises TypeError when deleting _wrapped."""
        class TestLazy(LazyObject):
            def _setup(self):
                self._wrapped = SimpleNamespace()

        obj = TestLazy()
        with self.assertRaises(TypeError) as context:
            delattr(obj, '_wrapped')

        assert "can't delete _wrapped." in str(context.exception)

    def test_lazy_object_delattr_triggers_setup_and_deletes_attr(self):
        """Test __delattr__ calls _setup when unevaluated and deletes attribute from wrapped."""
        class Inner:
            def __init__(self):
                self.FOO = 'bar'

        class TestLazy(LazyObject):
            def _setup(self):
                self._wrapped = Inner()

        obj = TestLazy()
        # _wrapped is unevaluated; deleting should trigger _setup then delete from wrapped
        delattr(obj, 'FOO')
        with self.assertRaises(AttributeError):
            _ = obj.FOO

    def test_lazy_object_setattr_triggers_setup_and_sets_attr(self):
        """Test __setattr__ calls _setup when unevaluated and sets attribute on wrapped."""
        class TestLazy(LazyObject):
            def _setup(self):
                self._wrapped = SimpleNamespace()

        obj = TestLazy()
        obj.NEW_ATTR = 'value'
        assert obj.NEW_ATTR == 'value'

    def test_lazy_settings_delattr_removes_attr_and_clears_cache(self):
        """Test LazySettings __delattr__ removes attribute from wrapped and clears cached value."""
        settings = LazySettings()
        setting = settings.TOKEN  # evaluate and cache
        assert settings.__dict__.get('TOKEN') == setting

        delattr(settings, 'TOKEN')
        assert 'TOKEN' not in settings.__dict__
        with self.assertRaises(AttributeError):
            _ = settings.TOKEN

    def test_lazy_settings_raises_without_env(self):
        """Test that LazySettings raises an error without HAMMETT_SETTINGS_MODULE
        environment variable.
        """
        with (
            patch.dict(os.environ, {}, clear=False),
            self.assertRaises(ImproperlyConfiguredError),
        ):
            os.environ.pop('HAMMETT_SETTINGS_MODULE', None)
            settings = LazySettings()

            # Accessing any attribute should trigger _setup and raise
            _ = settings.DOMAIN

    def test_lazy_settings_repr_evaluated(self):
        """Test LazySettings.__repr__ returns module name after evaluation."""
        settings = LazySettings()
        _ = settings.DOMAIN

        assert repr(settings) == '<LazySettings "tests.settings">'

    def test_lazy_settings_repr_unevaluated(self):
        """Test LazySettings.__repr__ returns Unevaluated when not set up."""
        settings = LazySettings()
        assert repr(settings) == '<LazySettings [Unevaluated]>'

    def test_lazy_settings_setattr_updates_value_and_clears_cache(self):
        """Test LazySettings __setattr__ updates wrapped value and returns updated on next get."""
        settings = LazySettings()
        assert 'IS_ADMIN' not in settings.__dict__

        _ = settings.IS_ADMIN  # trigger evaluation and cache
        assert 'IS_ADMIN' in settings.__dict__

        settings.IS_ADMIN = True
        assert 'IS_ADMIN' not in settings.__dict__
        assert settings.IS_ADMIN

    def test_lazyobject_requires_setup(self):
        """Test that LazyObject requires setup."""
        class TestSettings(LazyObject):
            pass

        settings = TestSettings()
        with self.assertRaises(NotImplementedError):
            settings._setup()

    def test_new_method_proxy_class_property_returns_wrapped_class(self):
        """Test that __class__ is proxied to the wrapped class via new_method_proxy."""
        class TestLazy(LazyObject):
            def _setup(self):
                self._wrapped = []

        obj = TestLazy()
        # __class__ should be the class of the wrapped object, not TestLazy
        assert obj.__class__ is list

    def test_new_method_proxy_triggers_setup_and_delegates_str(self):
        """Test that proxied __str__ triggers _setup and delegates to wrapped object."""
        class TestLazy(LazyObject):
            def _setup(self):
                self._wrapped = 'abc'

        obj = TestLazy()
        assert str(obj) == 'abc'

    def test_settings_check_hiders_checker_must_be_subclass(self):
        """Test that Settings checks that HIDERS_CHECKER_CLASS is a subclass."""
        module = SimpleNamespace(HIDERS_CHECKER_CLASS=object)
        with (
            patch('importlib.import_module', return_value=module),
            self.assertRaises(ImproperlyConfiguredError),
        ):
            Settings('tests.settings')

    def test_settings_check_permissions_must_be_list_or_tuple(self):
        """Test that Settings checks that PERMISSIONS is a list or tuple."""
        module = SimpleNamespace(PERMISSIONS=123)
        with (
            patch('importlib.import_module', return_value=module),
            self.assertRaises(ImproperlyConfiguredError),
        ):
            Settings('tests.settings')

    def test_settings_loads_and_overrides(self):
        """Test that Settings loads and overrides the settings."""
        settings = Settings('tests.settings')

        assert hasattr(settings, 'DOMAIN')  # default
        assert settings.TOKEN == 'secret-token'  # overridden in tests.settings

    def test_settings_repr(self):
        """Test that Settings.__repr__ returns the module name in the expected format."""
        settings = Settings('tests.settings')
        assert repr(settings) == "<Settings 'tests.settings'>"

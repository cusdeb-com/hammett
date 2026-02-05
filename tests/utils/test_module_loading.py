"""The module contains tests for the module loading helpers."""

from hammett.test.base import BaseTestCase
from hammett.utils.module_loading import import_string


class UtilsModuleLoadingTests(BaseTestCase):
    """The class implements tests for the module loading helpers."""

    def test_import_string_imports_attribute(self):
        """Test importing an attribute from a dotted path."""
        actual = import_string('hammett.test.base.BaseTestCase')
        assert actual is BaseTestCase

    def test_import_string_raises_on_invalid_path(self):
        """Test raising ImportError on invalid dotted path format."""
        with self.assertRaises(ImportError) as ctx:
            import_string('not_a_module_path')

        assert "doesn't look like a module path" in str(ctx.exception)

    def test_import_string_raises_on_missing_attribute(self):
        """Test raising ImportError when attribute does not exist in the module."""
        with self.assertRaises(ImportError) as ctx:
            import_string('importlib.nonexistent_attr')
        assert 'does not define a "nonexistent_attr"' in str(ctx.exception)

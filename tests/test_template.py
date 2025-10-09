"""The module contains the tests for the template helpers."""

from hammett.template import render_template_from_string
from hammett.test.base import BaseTestCase


class TemplateTests(BaseTestCase):
    """The class implements the tests for the template helpers."""

    def test_render_template_from_string_handles_html_entities(self):
        """Test that HTML entities are unescaped before rendering."""
        template = '5 &gt; 3 and {{ a }} &lt; {{ b }}'
        rendered = render_template_from_string(template, {'a': 1, 'b': 2})
        self.assertEqual(rendered, '5 > 3 and 1 < 2')

    def test_render_template_from_string_renders_variables(self):
        """Test rendering simple variables into a template string."""
        template = 'Hello, {{ name }}!'
        rendered = render_template_from_string(template, {'name': 'World'})
        self.assertEqual(rendered, 'Hello, World!')

    def test_render_template_from_string_works_with_none_context(self):
        """Test that None context is treated as empty dict."""
        template = 'Static text without variables'
        rendered = render_template_from_string(template, None)
        self.assertEqual(rendered, 'Static text without variables')

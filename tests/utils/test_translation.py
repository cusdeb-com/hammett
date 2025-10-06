"""The module contains tests for the translation helpers."""

# ruff: noqa: SLF001

import calendar
import gettext as native_gettext
from pathlib import Path
from unittest.mock import patch

from hammett.conf import settings
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from hammett.utils.translation import (
    HammettTranslation,
    _get_translation,
    _TranslationCatalog,
    gettext,
    ngettext,
)


class UtilsTranslationTests(BaseTestCase):
    """The class implements tests for translation helper functions/classes."""

    def test_adding_fallback_when_language_is_not_default(self):
        """Test adding a fallback when the language is not the default language."""
        with patch(
            'hammett.utils.translation.HammettTranslation.add_fallback',
        ) as mock_add_fallback:
            HammettTranslation('fr')
            mock_add_fallback.assert_called_once_with(_get_translation(settings.LANGUAGE_CODE))

    async def test_gettext_returns_original_when_missing(self):
        """Test gettext returns original caption when translation missing
        and language is provided.
        """
        unknown_key = 'unknown_key'
        self.assertEqual(gettext(unknown_key, language='en'), unknown_key)

    @override_settings(LANGUAGE_CODE='fr')
    async def test_gettext_uses_settings_language_code_when_language_not_provided(self):
        """Test gettext returns original caption when translation missing."""
        with patch('hammett.utils.translation._get_translation') as mock_get_translation:
            gettext('unknown_key')
            mock_get_translation.assert_called_once_with('fr')

    async def test_hammett_translation_merge_adds_entries(self):
        """Test merging external translations into the HammettTranslation catalog."""
        class DummyTranslations(native_gettext.GNUTranslations):
            def __init__(self):
                # Intentionally skip base __init__ to avoid file I/O
                self._catalog = {
                    'HELLO': 'Hola',
                    ('apples', 0): '1 manzana',
                    ('apples', 1): 'manzanas',
                }
                self.plural = lambda n: 0 if n == 1 else 1
                self._info = {}
                self._fallback = None

        translation = HammettTranslation('en')
        translation.merge(DummyTranslations())

        self.assertEqual(translation.gettext('HELLO'), 'Hola')
        self.assertEqual(translation.ngettext('apples', 'apples', 1), '1 manzana')
        self.assertEqual(translation.ngettext('apples', 'apples', 3), 'manzanas')

    def test_merge_adds_fallback_from_other_when_present(self):
        """Test that merge adds fallback from the other translations object when present."""
        class DummyTranslations(native_gettext.GNUTranslations):
            def __init__(self):
                self._catalog = {'HELLO': 'Hola'}
                self._info = {}
                self.plural = lambda n: 0 if n == 1 else 1
                self._fallback = object()

        with patch(
            'hammett.utils.translation.HammettTranslation.add_fallback',
        ) as mock_add_fallback:
            # Default language to avoid extra fallback from _add_fallback
            translation = HammettTranslation(settings.LANGUAGE_CODE)
            dummy = DummyTranslations()
            translation.merge(dummy)

            mock_add_fallback.assert_called_once_with(dummy._fallback)

    async def test_ngettext_returns_correct_form_without_catalog(self):
        """Test ngettext chooses singular/plural when no catalog mapping exists."""
        self.assertEqual(ngettext('apple', 'apples', 1, language='en'), 'apple')
        self.assertEqual(ngettext('apple', 'apples', 2, language='en'), 'apples')

    async def test_ngettext_uses_fallback_when_catalog_missing_entry(self):
        """Test that ngettext falls back to self._fallback.ngettext when plural key missing."""
        class DummyOther(native_gettext.GNUTranslations):
            def __init__(self):
                self._catalog = {}
                self.plural = lambda n: 0 if n == 1 else 1

        class DummyFallback:
            def ngettext(self, msgid1, msgid2, num):
                return f'fallback:{msgid1 if num == 1 else msgid2}:{num}'

        translation = HammettTranslation('fr')  # non-default language ensures fallback is allowed
        # Force _catalog to be _TranslationCatalog without the target keys
        translation._catalog = _TranslationCatalog(DummyOther())
        translation._fallback = DummyFallback()

        self.assertEqual(translation.ngettext('apples', 'apples', 2), 'fallback:apples:2')

    @override_settings(LOCALE_PATHS=[Path(__file__).parent / 'locale'])
    async def test_merges_for_each_locale_path_in_order(self):
        """Test that __init__ merges translations returned by _get_translation
        for each the LOCALE_PATHS entry.
        """
        translation = HammettTranslation('pt-br')
        self.assertIn('test', translation._catalog._catalogs[0])
        self.assertIn('ensaio', translation._catalog._catalogs[0].values())

    @override_settings(LANGUAGE_CODE='fr')
    async def test_ngettext_uses_settings_language_code_when_language_not_provided(self):
        """Test ngettext uses settings language code when language not provided."""
        with patch('hammett.utils.translation._get_translation') as mock_get_translation:
            ngettext('apple', 'apples', 1)
            mock_get_translation.assert_called_once_with('fr')

    async def test_setting_default_translation_catalog(self):
        """Test setting default translation catalog when domain is hammett."""
        translation = HammettTranslation('pt-br')
        catalog = translation._catalog._catalogs[0]
        for abbr in calendar.month_abbr:
            if abbr:  # skip empty string at index 0
                self.assertIn(abbr, catalog)


class UtilsTranslationCatalogTests(BaseTestCase):
    """The class implements tests for _TranslationCatalog behavior."""

    async def test_get_with_default_and_missing(self):
        """Test getting a value with a default and missing key."""
        catalog = _TranslationCatalog()
        self.assertIsNone(catalog.get('MISSING'))
        self.assertEqual(catalog.get('MISSING', 'default'), 'default')

    async def test_getitem_raises_keyerror_when_missing(self):
        """Test __getitem__ raises KeyError with the missing key value."""
        catalog = _TranslationCatalog()
        with self.assertRaises(KeyError) as ctx_str:
            catalog['MISSING']

        self.assertEqual(ctx_str.exception.args[0], 'MISSING')

        with self.assertRaises(KeyError) as ctx_tuple:
            catalog['apples', 0]

        self.assertEqual(ctx_tuple.exception.args[0], ('apples', 0))

    async def test_items_and_keys_iterate(self):
        """Test iterating over the catalog."""
        catalog = _TranslationCatalog()
        catalog['A'] = 'a'
        catalog['B'] = 'b'

        keys = set(catalog.keys())
        items = dict(catalog.items())
        self.assertTrue({'A', 'B'}.issubset(keys))
        self.assertTrue({'A': 'a', 'B': 'b'}.items() <= items.items())

    async def test_plural_returns_value_or_raises(self):
        """Test returning a value or raising an error for plural forms."""
        class DummyTranslations(native_gettext.GNUTranslations):
            def __init__(self):
                self._catalog = {('apples', 0): '1 apple', ('apples', 1): 'apples'}
                self.plural = lambda n: 0 if n == 1 else 1

        catalog = _TranslationCatalog(DummyTranslations())
        self.assertEqual(catalog.plural('apples', 1), '1 apple')
        self.assertEqual(catalog.plural('apples', 3), 'apples')

    async def test_set_and_get_and_contains(self):
        """Test setting, getting, and checking for keys in the catalog."""
        catalog = _TranslationCatalog()
        catalog['HELLO'] = 'Hola'
        catalog['apples', 0] = '1 manzana'
        catalog['apples', 1] = 'manzanas'

        self.assertIn('HELLO', catalog)
        self.assertIn(('apples', 0), catalog)
        self.assertEqual(catalog['HELLO'], 'Hola')
        self.assertEqual(catalog['apples', 1], 'manzanas')

    async def test_update_overrides_previous_catalog(self):
        """Test updating the catalog with a new value."""
        class DummyTranslations(native_gettext.GNUTranslations):
            def __init__(self, value: str):
                self._catalog = {'KEY': value}
                self.plural = lambda n: 0 if n == 1 else 1

        catalog = _TranslationCatalog(DummyTranslations('first'))
        self.assertEqual(catalog['KEY'], 'first')

        catalog.update(DummyTranslations('second'))
        self.assertEqual(catalog['KEY'], 'second')

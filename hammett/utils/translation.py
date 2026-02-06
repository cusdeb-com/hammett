# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The module contains tools for localization."""

# ruff: noqa: SLF001

import contextlib
import gettext as native_gettext
import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Self

_translations = {}


def _get_translation(language: str) -> 'HammettTranslation':
    """Return a translation object based on the language.

    Returns:
        Translation object.

    """
    if language not in _translations:
        _translations[language] = HammettTranslation(language)

    return _translations[language]


def gettext(caption: str, language: str = '') -> str:
    """Return translated text by its caption.

    Returns:
        Translated text by its caption.

    """
    if not language:
        from hammett.conf import settings

        language = settings.LANGUAGE_CODE

    return _get_translation(language).gettext(caption)


def ngettext(singular: str, plural: str, num: int, language: str = '') -> str:
    """Return the translated singular or plural form based on the language and number.

    Returns:
        Translated singular or plural form.

    """
    if not language:
        from hammett.conf import settings

        language = settings.LANGUAGE_CODE

    return _get_translation(language).ngettext(singular, plural, num)


class HammettTranslation(native_gettext.GNUTranslations):
    """The class implements an interface for managing translations."""

    def __init__(self: 'Self', language: str) -> None:
        """Initialize a translation object."""
        from hammett.conf import settings

        super().__init__()

        self._catalog: _TranslationCatalog | dict[str, str] = {}
        self._domain = settings.DOMAIN
        self._language = language
        self.plural = lambda n: int(n != 1)

        if self._domain == 'hammett':
            self._init_translation_catalog(language)

        if settings.LOCALE_PATHS:
            for localedir in settings.LOCALE_PATHS:
                self.merge(self._get_translation(language, localedir))

        self._add_fallback()

    def _add_fallback(self: 'Self') -> None:
        """Add the fallback."""
        from hammett.conf import settings

        # Don't set a fallback for the default language or any English variant
        if self._language == settings.LANGUAGE_CODE or self._language.startswith('en'):
            return

        self.add_fallback(_get_translation(settings.LANGUAGE_CODE))

    def _init_translation_catalog(self: 'Self', language: str) -> None:
        """Initialize a catalog with a default translation."""
        from hammett.conf import settings

        settings_module = sys.modules[settings.__module__].__file__
        if settings_module is not None:
            self.merge(self._get_translation(language, Path(settings_module).parent / 'locale'))

    def _get_translation(
        self: 'Self',
        language: str,
        localedir: 'str | Path',
        *,
        use_null_fallback: bool = True,
    ) -> 'native_gettext.GNUTranslations':
        """Create and return a translation object.

        Returns:
            Created translation object.

        """
        return cast(
            'native_gettext.GNUTranslations',
            native_gettext.translation(
                domain=self._domain,
                localedir=localedir,
                languages=[language],
                fallback=use_null_fallback,
            ),
        )

    def merge(self: 'Self', other: 'native_gettext.GNUTranslations') -> None:
        """Merge the given translations into the current catalog."""
        if not getattr(other, '_catalog', None):
            return

        if isinstance(self._catalog, _TranslationCatalog):
            self._catalog.update(other)
        else:
            self.plural = other.plural  # type: ignore[attr-defined]
            self._info = other._info.copy()  # type: ignore[attr-defined]
            self._catalog = _TranslationCatalog(other)

        if other._fallback:  # type: ignore[attr-defined]
            self.add_fallback(other._fallback)  # type: ignore[attr-defined]

    def ngettext(self: 'Self', msgid1: str, msgid2: str, num: int) -> str:
        """Return translated text according to the language and the counting number.

        Returns:
            Translated text according to the language and the counting number.

        """
        message = msgid1 if num == 1 else msgid2
        try:
            if isinstance(self._catalog, _TranslationCatalog):
                message = self._catalog.plural(msgid1, num)
        except KeyError:
            if getattr(self, '_fallback', None):
                return cast('str', self._fallback.ngettext(msgid1, msgid2, num))  # type: ignore[attr-defined]

        return message


class _TranslationCatalog:
    """The class implements a dictionary that allows storing multiple
    translation catalogs.
    """

    def __init__(
        self: 'Self',
        translations: 'native_gettext.GNUTranslations | None' = None,
    ) -> None:
        """Initialize a translation catalog object."""
        self._catalogs: list[dict[str, str] | dict[tuple[str, int], str]] = (
            [{}] if translations is None else [translations._catalog.copy()]  # type: ignore[attr-defined]
        )
        self._plurals: list[Callable[[int], int]] = (
            [lambda n: int(n != 1)] if translations is None else [translations.plural]  # type: ignore[attr-defined]
        )

    def __contains__(self, key: str | tuple[str, int]) -> bool:
        """Check whether the key exists.

        Returns:
            The result of checking whether the key exists.

        """
        return any(key in catalog for catalog in self._catalogs)

    def __getitem__(self: 'Self', key: str | tuple[str, int]) -> str:
        """Return the first found value of the key.

        Returns:
            Found value of the key.

        Raises:
            KeyError: If the key hasn't been found.

        """
        for catalog in self._catalogs:
            with contextlib.suppress(KeyError):
                if isinstance(key, str):
                    return cast('dict[str, str]', catalog)[key]

                return cast('dict[tuple[str, int], str]', catalog)[key]

        raise KeyError(key)

    def __setitem__(self: 'Self', key: str | tuple[str, int], value: str) -> None:
        """Set the value to the key."""
        if isinstance(key, str):
            cast('dict[str, str]', self._catalogs[0])[key] = value
        else:
            cast('dict[tuple[str, int], str]', self._catalogs[0])[key] = value

    def get(self: 'Self', key: tuple[str, int] | str, default: str | None = None) -> str | None:
        """Return the value of the key.

        Returns:
            Value of the key.

        """
        for catalog in self._catalogs:
            result = (
                cast('dict[str, str]', catalog).get(key)
                if isinstance(key, str)
                else cast('dict[tuple[str, int], str]', catalog).get(key)
            )
            if result is not None:
                return result

        return default

    def items(
        self: 'Self',
    ) -> 'Generator[tuple[str, str] | tuple[tuple[str, int], str], None, None]':
        """Yield the items.

        Yields:
            Items.

        """
        for catalog in self._catalogs:
            yield from catalog.items()

    def keys(self: 'Self') -> 'Generator[str | tuple[str, int], None, None]':
        """Yield the keys.

        Yields:
            Keys.

        """
        for catalog in self._catalogs:
            yield from catalog.keys()

    def plural(self: 'Self', msgid: str, num: int) -> str:
        """Return a message based on the msgid and number.

        Returns:
            Message based on the msgid and number.

        Raises:
            KeyError: If the message hasn't been found.

        """
        for catalog, plural in zip(self._catalogs, self._plurals, strict=False):
            message = cast('dict[tuple[str, int], str]', catalog).get((msgid, plural(num)))
            if message is not None:
                return message

        raise KeyError

    def update(self: 'Self', translation: 'native_gettext.GNUTranslations') -> None:
        """Add a new translation catalog to the existing list."""
        self._catalogs.insert(0, translation._catalog.copy())  # type: ignore[attr-defined]
        self._plurals.insert(0, translation.plural)  # type: ignore[attr-defined]

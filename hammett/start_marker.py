"""The module contains a start-markers parser."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import ItemsView, KeysView, ValuesView
    from typing import Self


class StartMarker:
    """The class implements a start-markers parser."""

    def __init__(self: 'Self', start_marker: str) -> None:
        """Initialize a start-markers parser object."""
        self._start_marker = start_marker
        self._result: dict[str, str] = {}

        self._parse()

    def __getitem__(self: 'Self', item: str) -> str:
        """Return an element by a key.

        Returns:
            Element by a passed key.

        """
        return self._result[item]

    def _parse(self: 'Self') -> None:
        """Parse start-makers."""
        markers = self._start_marker[len('/start ') :]
        if markers:
            parts = markers.removeprefix('=').removesuffix('=').split('=')
            if len(parts) % 2 != 0:
                parts = ['source', *parts]

            keys = parts[::2]
            values = parts[1::2]
            self._result = dict(zip(keys, values, strict=False))

    def items(self: 'Self') -> 'ItemsView[str, str]':
        """Return a dictionary with start markers as items.

        Returns:
            Items of the dictionary with start markers.

        """
        return self._result.items()

    def keys(self: 'Self') -> 'KeysView[str]':
        """Return a dictionary with start-markers as keys.

        Returns:
            Keys of the dictionary with start markers.

        """
        return self._result.keys()

    def pop(self: 'Self', key: str, default: str | None = None) -> str:
        """Remove specified key and return the corresponding value.

        Returns:
            Element by a passed key.

        Raises:
            KeyError: If the key is not found and default value is not given
            raise a KeyError.

        """
        try:
            return self._result.pop(key)
        except KeyError:
            if default is None:
                raise

            return default

    def values(self: 'Self') -> 'ValuesView[str]':
        """Return a dictionary with start-markers as values.

        Returns:
            Values of the dictionary with start markers.

        """
        return self._result.values()

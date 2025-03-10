"""The module contains a start-markers parser."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

        Returns
        -------
            Element by a passed key.

        """
        return self._result[item]

    def _parse(self: 'Self') -> None:
        """Parse start-makers."""
        markers = self._start_marker[len('/start '):]
        if markers:
            parts = markers.removeprefix('=').removesuffix('=').split('=')
            if len(parts) % 2 != 0:
                parts = ['source', *parts]

            keys = parts[::2]
            values = parts[1::2]
            self._result = dict(zip(keys, values, strict=False))

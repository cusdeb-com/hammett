"""The module contains functions for working with dynamic descriptions."""

import html
from typing import TYPE_CHECKING

from jinja2 import BaseLoader, Environment

if TYPE_CHECKING:
    from typing import Any


def render_template_from_string(template: str, context: dict[str, 'Any'] | None = None) -> str:
    """Return a description after formatting it using passed data.

    Returns
    -------
        Formatted description with passed data.

    """
    return Environment(  # noqa: S701
        loader=BaseLoader(),
    ).from_string(
        html.unescape(template),
    ).render(
        **({} if context is None else context),
    )

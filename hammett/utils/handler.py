"""The module contains tools for working with handlers."""

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hammett.types import HANDLER_ASSIGNMENTS_TYPE, Func

HANDLER_ASSIGNMENTS = (*functools.WRAPPER_ASSIGNMENTS, '__self__')


def wraps_handler(
    wrapped: 'Func',
    assigned: 'HANDLER_ASSIGNMENTS_TYPE' = HANDLER_ASSIGNMENTS,
    updated: tuple[str] = functools.WRAPPER_UPDATES,
) -> 'functools.partial[Func]':
    """Represent a decorator factory which is identical to `functools.wraps`.
    The only thing is different is the `assigned` argument. It is required for the
    `calc_checksum` function to return a valid result even for a decorated handler.
    The decorator factory should be used if a custom decorator for the handler is implemented.

    Returns
    -------
        New function with partial application of the given arguments and keywords.

    """
    return functools.partial(  # type: ignore[return-value]
        functools.update_wrapper,  # type: ignore[arg-type]
        wrapped=wrapped,
        assigned=assigned,
        updated=updated,
    )

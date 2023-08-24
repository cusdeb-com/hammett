"""The module contains the routine for autodiscovering screens
(i.e., subclasses of the Screen class).
"""

import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

from hammett.core.permissions import Permission
from hammett.core.screen import Screen

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import ModuleType


def _autodiscover_screens_in_module(
    module: 'ModuleType',
    exclude_screens: 'Iterable[type[Screen]]',
) -> 'set[type[Screen]]':
    """Looks through the specified module for subclasses of the Screen class.
    The function skips the Permission subclasses and Screen itself.
    """

    return {
        obj for _, obj in inspect.getmembers(module)
        if inspect.isclass(obj)
        # Permission classes subclass Screen,
        # but their handlers do not need to be registered,
        # so explicitly skip these classes.
        and not issubclass(obj, Permission)
        and issubclass(obj, Screen)
        and obj is not Screen
        and obj not in exclude_screens
    }


def autodiscover_screens(
    package_name: str,
    exclude_screens: 'Iterable[type[Screen]] | None' = None,
) -> 'set[type[Screen]]':
    """Automatically discovers screens (i.e., subclasses of the Screen class),
    looking them in the specified package.
    """

    if exclude_screens is None:
        exclude_screens = []

    subclasses = set()

    target = importlib.import_module(package_name)
    subclasses.update(_autodiscover_screens_in_module(target, exclude_screens))

    for _, module_name, is_pkg in pkgutil.walk_packages(target.__path__):
        path = f'{package_name}.{module_name}'

        if is_pkg:
            package = importlib.import_module(path)
            subclasses.update(_autodiscover_screens_in_module(package, exclude_screens))
            subclasses.update(autodiscover_screens(path, exclude_screens))
        else:
            module = importlib.import_module(path)
            subclasses.update(_autodiscover_screens_in_module(module, exclude_screens))

    return subclasses

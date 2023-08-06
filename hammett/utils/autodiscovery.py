"""The module contains the routine for autodiscovering screens
(i.e., subclasses of the Screen class).
"""

import importlib
import inspect
import pkgutil
from types import ModuleType

from hammett.core.screen import Screen


def _autodiscover_screens_in_module(module: ModuleType) -> set[type[Screen]]:
    """Looks through the specified module for subclasses of the Screen class.
    The function skips Screen itself.
    """

    return {
        obj for _, obj in inspect.getmembers(module)
        if inspect.isclass(obj) and issubclass(obj, Screen) and obj is not Screen
    }


def autodiscover_screens(package_name: str) -> list[type[Screen]]:
    """Automatically discovers screens (i.e., subclasses of the Screen class),
    looking them in the specified package.
    """

    subclasses = set()

    target = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.walk_packages(target.__path__):
        path = f'{package_name}.{module_name}'

        if is_pkg:
            package = importlib.import_module(path)
            subclasses.update(_autodiscover_screens_in_module(package))
            subclasses.update(autodiscover_screens(path))
        else:
            module = importlib.import_module(path)
            subclasses.update(_autodiscover_screens_in_module(module))

    return list(subclasses)

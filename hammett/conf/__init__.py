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
"""The module contains facilities for working with settings of the projects based
on Hammett.

hammett.conf.global_settings acts as a source for the settings and their
default values. Then, the values can be overridden using the module
specified via the HAMMETT_SETTINGS_MODULE environment variable.

See the global_settings.py for a list of all possible settings.
"""

import importlib
import operator
import os
from typing import TYPE_CHECKING

from hammett.conf import global_settings
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.hiders import HidersChecker

if TYPE_CHECKING:
    from typing import Any

    from typing_extensions import Self

    from hammett.types import Func

_EMPTY = object()

_HAMMETT_SETTINGS_MODULE = 'HAMMETT_SETTINGS_MODULE'


def new_method_proxy(func: 'Func') -> 'Any':
    """Route functions to the _wrapped object."""
    # It's necessary to use the wraps decorator when wrapping functions.
    # But not here. The point is that new_method_proxy is used mainly with
    # the magic methods which, as a rule, are not used directly. So, avoiding
    # using the decorator here can be considered as optimization.

    def inner(self: 'LazyObject', *args: 'Any') -> 'Any':
        if self._wrapped is _EMPTY:
            self._setup()

        return func(self._wrapped, *args)
    return inner


class GlobalSettings:
    """The class implements a simple interface for accessing
    the global settings.
    """

    def __getattr__(self: 'Self', name: str) -> 'Any':
        """Return the value of a global setting."""
        return getattr(global_settings, name)

    def __repr__(self: 'Self') -> str:
        """Return a system representation of a global setting."""
        return f'<{self.__class__.__name__}>'


class LazyObject:
    """The class implements a wrapper for another class that can be used to delay
    instantiation of the wrapped class.
    """

    # Avoid infinite recursion when tracing __init__.
    _wrapped: 'Settings | object' = _EMPTY

    def __init__(self: 'Self') -> None:
        """Initialize a lazy object."""
        # Note: if a subclass overrides __init__(), it will likely need to
        # override __copy__() and __deepcopy__() as well.
        self._wrapped = _EMPTY

    def _setup(self: 'Self') -> None:
        """Initialize the wrapped object."""
        msg = 'subclasses of LazyObject must provide a _setup() method.'
        raise NotImplementedError(msg)

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self: 'Self', name: str, value: 'Any') -> None:
        """Set the value of a lazy object."""
        if name == '_wrapped':
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__['_wrapped'] = value
        else:
            if self._wrapped is _EMPTY:
                self._setup()

            setattr(self._wrapped, name, value)

    def __delattr__(self: 'Self', name: str) -> None:
        """Delete a lazy object."""
        if name == '_wrapped':
            msg = "can't delete _wrapped."
            raise TypeError(msg)

        if self._wrapped is _EMPTY:
            self._setup()

        delattr(self._wrapped, name)

    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)

    # Introspection support.
    __dir__ = new_method_proxy(dir)

    # Pretend to be the wrapped class.
    __class__ = property(
        new_method_proxy(operator.attrgetter('__class__')),  # type: ignore[assignment]
    )
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __gt__ = new_method_proxy(operator.gt)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)

    # List/Tuple/Dictionary methods support.
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


class LazySettings(LazyObject):
    """The class implements a lazy proxy for Hammett settings.
    Hammett uses the settings module specified via the HAMMETT_SETTINGS_MODULE
    environment variable.
    """

    def _setup(self: 'Self', name: str | None = None) -> None:
        """Load the settings module specified via the HAMMETT_SETTINGS_MODULE
        environment variable. This is used the first time settings are needed,
        if the user hasn't configured settings manually.
        """
        settings_module = os.environ.get(_HAMMETT_SETTINGS_MODULE)
        if not settings_module:
            desc = f'setting {name}' if name else 'settings'
            msg = (
                f'Requested {desc}, but settings are not configured. '
                f'You must either define the environment variable '
                f'{_HAMMETT_SETTINGS_MODULE} or call settings.configure() '
                f'before accessing settings.'
            )
            raise ImproperlyConfigured(msg)

        self._wrapped = Settings(settings_module)

    def __repr__(self: 'Self') -> str:
        """Return a system representation of a lazy setting."""
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is _EMPTY:
            return '<LazySettings [Unevaluated]>'

        return (
            f'<LazySettings "{self._wrapped.settings_module_name}">'  # type: ignore[attr-defined]
        )

    def __getattr__(self: 'Self', name: str) -> 'Any':
        """Return the value of a setting and caches it in self.__dict__."""
        if self._wrapped is _EMPTY:
            self._setup(name)

        val = getattr(self._wrapped, name)
        self.__dict__[name] = val

        return val

    def __setattr__(self: 'Self', name: str, value: 'Any') -> None:
        """Set the value of setting. Clear all cached values if _wrapped changes
        (@override_settings does this) or clears single values when set.
        """
        if name == '_wrapped':
            self.__dict__.clear()
        else:
            self.__dict__.pop(name, None)

        super().__setattr__(name, value)

    def __delattr__(self: 'Self', name: str) -> None:
        """Delete a setting and clear it from cache if needed."""
        super().__delattr__(name)
        self.__dict__.pop(name, None)


class Settings:
    """The class implements the interface for working with settings of
    the projects based on Hammett.
    """

    def __init__(self: 'Self', settings_module: str) -> None:
        """Initialize a settings object."""
        self.settings_module_name = settings_module

        self._explicit_settings = set()
        self._settings_module = importlib.import_module(self.settings_module_name)

        # update this dict from global settings (but only for ALL_CAPS settings)
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

        for setting in dir(self._settings_module):
            if setting.isupper():
                setting_value = getattr(self._settings_module, setting)

                setattr(self, setting, setting_value)
                self._explicit_settings.add(setting)

        self._check()

    def _check(self: 'Self') -> None:
        """Check the settings for gross errors."""
        if self._is_overridden('HIDERS_CHECKER_CLASS'):
            setting_value = getattr(self._settings_module, 'HIDERS_CHECKER_CLASS')  # noqa: B009
            if not isinstance(setting_value, type) or not issubclass(setting_value, HidersChecker):
                msg = 'HIDERS_CHECKER_CLASS must be a subclass of HidersChecker'
                raise ImproperlyConfigured(msg)

        if self._is_overridden('PERMISSIONS'):
            setting_value = getattr(self._settings_module, 'PERMISSIONS')  # noqa: B009
            if not isinstance(setting_value, list | tuple):
                msg = "The 'PERMISSIONS' setting must be a list or a tuple."
                raise ImproperlyConfigured(msg)

    def _is_overridden(self: 'Self', setting: str) -> bool:
        """Check if the specified setting is overriden."""
        return setting in self._explicit_settings

    def __repr__(self: 'Self') -> str:
        """Return a system representation of a setting."""
        return f"<{self.__class__.__name__} '{self.settings_module_name}'>"


settings = LazySettings()

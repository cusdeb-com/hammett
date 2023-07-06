"""
The module contains facilities for working with settings of the projects based
on Hammett.

hammett.conf.global_settings acts as a source for the settings and their
default values. Then, the values can be overridden using the module
specified via the HAMMETT_SETTINGS_MODULE environment variable.

See the global_settings.py for a list of all possible settings.
"""

import importlib
import os

from hammett.conf import global_settings
from hammett.core.exceptions import ImproperlyConfigured
from hammett.core.hiders import HidersChecker

_HAMMETT_SETTINGS_MODULE = 'HAMMETT_SETTINGS_MODULE'


class Settings:
    """The class implements the interface for working with settings of
    the projects based on Hammett.
    """
    
    def __init__(self):
        self._explicit_settings = set()
        self._settings_module_name = os.environ.get(_HAMMETT_SETTINGS_MODULE)
        if not self._settings_module_name:
            msg = 'Config failed'
            raise ImproperlyConfigured(msg)

        self._settings_module = importlib.import_module(self._settings_module_name)

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

    def _check(self):
        """Checks the settings for gross errors. """

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

    def _is_overridden(self, setting):
        """Checks if the specified setting is overriden. """

        return setting in self._explicit_settings

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self._settings_module_name}'>"


settings = Settings()

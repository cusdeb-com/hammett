"""
The module contains the exception and warning classes
related to the widget library.
"""


class ChoiceEmojisAreUndefined(Exception):
    """
    Raised when a widget inherits from the base class and
    forgets to specify the choice emojis.
    """


class ChoicesFormatIsInvalid(Exception):
    """Raised when choices are specified but their format is invalid."""


class FailedToGetStateKey(Exception):
    """Raised when the attempt to get a widget state key fails."""


class MissingPersistence(Exception):
    """
    Raised when some feature requires persistence,
    but it's not configured.
    """


class NoChoicesSpecified(Exception):
    """
    Raised when a widget inherits from the base class and
    forgets to specify choices.
    """

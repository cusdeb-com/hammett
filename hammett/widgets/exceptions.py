"""The module contains the exception and warning classes
related to the widget library.
"""


class ChoiceEmojisAreUndefinedError(Exception):
    """Raised when a widget inherits from the base class and
    forgets to specify the choice emojis.
    """


class ChoicesFormatIsInvalidError(Exception):
    """Raised when choices are specified but their format is invalid."""


class FailedToGetStateKeyError(Exception):
    """Raised when the attempt to get a widget state key fails."""


class NoChoicesSpecifiedError(Exception):
    """Raised when a widget inherits from the base class and
    forgets to specify choices.
    """

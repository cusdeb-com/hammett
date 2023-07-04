"""The module contains the global Hammett exception and warning classes. """


class ImproperlyConfigured(Exception):
    """Raised when Hammett is somehow improperly configured. """


class HiderIsUnregistered(Exception):
    """Raised when an unregistered hider is used. """


class TokenIsNotSpecified(Exception):
    """Raised when the token is not specified. """


class UnknownSourceType(Exception):
    """Raised when an unknown source type is specified for an inline button. """

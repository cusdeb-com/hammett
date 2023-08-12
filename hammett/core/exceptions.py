"""The module contains the global Hammett exception and warning classes."""


class FailedToGetDataAttributeOfQuery(Exception):
    """Raised when the attempt to get a data attribute of a query fails."""


class ImproperlyConfigured(Exception):
    """Raised when Hammett is somehow improperly configured."""


class HiderIsUnregistered(Exception):
    """Raised when an unregistered hider is used."""


class PayloadTooLong(Exception):
    """Raised when a payload passed through a button is too long."""


class TokenIsNotSpecified(Exception):
    """Raised when the token is not specified."""


class UnknownSourceType(Exception):
    """Raised when an unknown source type is specified for an inline button."""

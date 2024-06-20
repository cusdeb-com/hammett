"""The module contains the global Hammett exception and warning classes."""


class CommandNameIsEmpty(Exception):
    """Raised when trying to register a handler for
    a command with an empty name (i.e., '/').
    """


class FailedToGetDataAttributeOfQuery(Exception):
    """Raised when the attempt to get a data attribute of a query fails."""


class LocalePathIsNotSpecified(Exception):
    """Raised when the locale path is not specified."""


class ImproperlyConfigured(Exception):
    """Raised when Hammett is somehow improperly configured."""


class HiderIsUnregistered(Exception):
    """Raised when an unregistered hider is used."""


class MissingPersistence(Exception):
    """Raised when some feature requires persistence,
    but it's not configured.
    """


class PayloadIsEmpty(Exception):
    """Raised when trying to get an empty payload."""


class ScreenDescriptionIsEmpty(Exception):
    """Raised when attempting to render a screen, but the description
    of the screen is found to be empty.
    """


class ScreenDocumentDataIsEmpty(Exception):
    """Raised when attempting to send a screen with a document,
    but the document data of the screen is found to be empty.
    """


class ScreenRouteIsEmpty(Exception):
    """Raised when the route of the route mixin is found
    to be empty.
    """


class StatesAttributeIsNotSupported(Exception):
    """Raised when the states attribute of the register_button_handler
    is not supported by HandlerType.
    """


class TokenIsNotSpecified(Exception):
    """Raised when the token is not specified."""


class UnknownHandlerType(Exception):
    """Raised when an unknown type is specified for a handler."""


class UnknownSourceType(Exception):
    """Raised when an unknown source type is specified for an inline button."""

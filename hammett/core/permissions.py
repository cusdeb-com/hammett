"""The module contains the implementation of the permissions mechanism. """

from functools import wraps
from uuid import uuid4


def ignore_permissions(permissions):
    """The decorator is intended for decorating Screen methods to specify
    which permissions they are allowed to ignore.
    """

    def decorator(func):
        func.permissions_ignored = [permission.CLASS_UUID for permission in permissions]

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


class Permission:
    """The base class for the implementations of custom permissions. """

    CLASS_UUID = uuid4()

    def check_permission(self, handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            """"""

            if self.has_permission(*args, **kwargs):
                return handler(*args, **kwargs)

            return self.handle_permission_denied(*args, **kwargs)

        return wrapper

    def handle_permission_denied(self, update, context):
        """Invoked in case of `has_permission` returns False. """

        raise NotImplemented

    def has_permission(self, update, context):
        """Invoked before running each Screen method to check a permission. """

        raise NotImplemented

"""The module contains the settings for the tests."""

IS_ADMIN = False

IS_MODERATOR = False

PERMISSIONS = [
    'tests.test_permissions_mechanism.MainPermission',
    'tests.test_permissions_mechanism.SubPermission',
]

TOKEN = 'secret-token'  # noqa: S105

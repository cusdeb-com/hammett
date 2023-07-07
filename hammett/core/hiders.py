"""The module contains the implementation of the hiders mechanism. """

from typing import TYPE_CHECKING

from hammett.core.exceptions import HiderIsUnregistered

if TYPE_CHECKING:
    from typing import Self

    from telegram import Update
    from telegram.ext import CallbackContext

(
    ONLY_FOR_ADMIN,
    ONLY_FOR_BETA_TESTERS,
    ONLY_FOR_MODERATORS,
) = range(3)


class Hider:
    def __init__(self: 'Self', hider: 'Hider') -> None:
        self.hider: 'Hider' = hider
        self.hiders_set: set['Hider'] = {hider}

    def __or__(self: 'Self', other: 'Hider') -> 'Self':
        self.hiders_set.add(other.hider)
        return self


class HidersChecker:
    def __init__(self: 'Self', hiders_set: set[Hider]) -> None:
        if getattr(self, 'custom_hiders', None) is None:
            self.custom_hiders = {}

        self._hiders_set = hiders_set
        self._registered_hiders = {}
        self._register_hiders()

    #
    # Private methods
    #

    def _register_hiders(self: 'Self') -> None:
        self._registered_hiders = {
            ONLY_FOR_ADMIN: self.is_admin,
            ONLY_FOR_BETA_TESTERS: self.is_beta_tester,
            ONLY_FOR_MODERATORS: self.is_moderator,
            **self.custom_hiders,
        }

    #
    # Public methods
    #

    async def is_admin(self: 'Self', _update: 'Update', _context: 'CallbackContext') -> bool:
        """A stub for checking whether the user is an admin. """

        return False

    async def is_beta_tester(self: 'Self', _update: 'Update', _context: 'CallbackContext') -> bool:
        """A stub for checking whether the user is a beta tester. """

        return False

    async def is_moderator(self: 'Self', _update: 'Update', _context: 'CallbackContext') -> bool:
        """A stub for checking whether the user is a moderator. """

        return False

    async def run(self: 'Self', update: 'Update', context: 'CallbackContext') -> bool:
        for hider in self._hiders_set:
            try:
                hider_handler = self._registered_hiders[hider]
            except KeyError as exc:
                msg = f"The hider '{hider}' is unregistered"
                raise HiderIsUnregistered(msg) from exc

            if await hider_handler(update, context):
                return True

        return False

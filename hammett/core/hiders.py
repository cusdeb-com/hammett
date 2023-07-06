"""The module contains the implementation of the hiders mechanism. """

from hammett.core.exceptions import HiderIsUnregistered

(
    ONLY_FOR_ADMIN,
    ONLY_FOR_BETA_TESTERS,
    ONLY_FOR_MODERATORS,
) = range(3)


class Hider:
    def __init__(self, hider):
        self.hider = hider
        self.hiders_set = {hider}

    def __or__(self, other):
        self.hiders_set.add(other.hider)
        return self


class HidersChecker:
    def __init__(self, hiders_set):
        if getattr(self, 'custom_hiders', None) is None:
            self.custom_hiders = {}

        self._hiders_set = hiders_set
        self._registered_hiders = {}
        self._register_hiders()

    #
    # Private methods
    #

    def _register_hiders(self):
        self._registered_hiders = {
            ONLY_FOR_ADMIN: self.is_admin,
            ONLY_FOR_BETA_TESTERS: self.is_beta_tester,
            ONLY_FOR_MODERATORS: self.is_moderator,
            **self.custom_hiders,
        }

    #
    # Public methods
    #

    async def is_admin(self, update, context) -> bool:
        """A stub for checking whether the user is an admin. """

        return False

    async def is_beta_tester(self, update, context) -> bool:
        """A stub for checking whether the user is a beta tester. """

        return False

    async def is_moderator(self, update, context) -> bool:
        """A stub for checking whether the user is a moderator. """

        return False

    async def run(self, update, context):
        for hider in self._hiders_set:
            try:
                hider_handler = self._registered_hiders[hider]
            except KeyError:
                raise HiderIsUnregistered(
                    f"The hider '{hider}' is unregistered",
                )

            if await hider_handler(update, context):
                return True
        else:
            return False

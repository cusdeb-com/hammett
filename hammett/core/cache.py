"""The module contains tools for caching."""

import pickle
from functools import wraps
from typing import TYPE_CHECKING, Any

import redis.asyncio as redis

from hammett.conf import settings
from hammett.core.exceptions import ImproperlyConfiguredError

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Self

CACHE_REDIS_CLI: 'redis.Redis[Any]' = redis.Redis(
    **{key.lower(): val for key, val in settings.REDIS_CACHE.items()},
)


def cache(ttl: int) -> 'Callable[[Any], Any]':
    """Cache the result of the decorated function.

    Returns:
        Wrapped decorated function.

    """

    def decorator(func: 'Callable[[Any], Any]') -> 'Callable[[Any], Any]':
        try:
            settings.REDIS_CACHE['DB']
        except KeyError as exc:
            msg = f'{exc.args[0]} is missing in REDIS_CACHE setting'
            raise ImproperlyConfiguredError(msg) from exc

        @wraps(func)
        async def wrapper(self: 'Self', *args: 'Any', **kwargs: 'Any') -> 'Any':  # type: ignore[misc]
            drop_cache = kwargs.pop('drop_cache', False)

            key = f'{func.__name__}:{pickle.dumps(args)!r}:{pickle.dumps(kwargs)!r}'
            res = await CACHE_REDIS_CLI.get(key)
            if res and not drop_cache:
                res = pickle.loads(res)
            else:
                res = await func(self, *args, **kwargs)
                await CACHE_REDIS_CLI.set(key, pickle.dumps(res), ttl)

            return res

        return wrapper

    return decorator

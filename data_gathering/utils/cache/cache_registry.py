import logging
from functools import wraps
from threading import RLock
from typing import Any, Callable, Type

from .cache import Cache

type CacheMethod = Callable[..., Any]
type CacheDecorator = Callable[..., Any]

logger = logging.getLogger(__name__)


class CacheRegistry:
    """Registry to store and retrieve decorated cache objects"""

    def __init__(self) -> None:
        self._cache_objects: dict[Type[Cache], Cache] = {}
        self._locks: dict[Type[Cache], RLock] = {}
        self._global_lock = RLock()

    def cache_decorator(self, cache_class: Type[Cache]) -> Any:
        """
        Decorator to wrap functions with cache handling.

        Ensures the cache is synced and closed after the function call.

        :param func: Function to be wrapped
        :return: Wrapped function
        """

        def decorator(func: CacheMethod) -> Any:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # Use the registry to get the decorated cache object
                cache_obj = self.get_cache(cache_class)
                try:
                    # Call the wrapped function with the cache
                    return func(cache_obj, *args, **kwargs)
                finally:
                    # ensure we sync and close the cache
                    cache_obj.sync()
                    cache_obj.close()

            return wrapper

        return decorator

    def get_cache(self, cache_class: Type[Cache]) -> Cache:
        """
        Retrieve or create a cache object of the specified class.

        If a cache object of the specified class does not exist, a new instance is created and returned.

        If the provided class is not a subclass of Cache, a warning is logged.

        :param cache_class: The class of the cache object to retrieve or create.
        :return: The cache object of the specified class.
        """
        if not issubclass(cache_class, Cache):
            logger.warning(
                f"{cache_class} is not a subclass of Cache. Caching with this object may not work properly."
            )
            return None

        lock = self.get_lock(cache_class)
        acquired = lock.acquire(blocking=False)
        try:
            if cache_class not in self._cache_objects:
                cache_obj = cache_class()
                self._cache_objects[cache_class] = cache_obj
        finally:
            if acquired:
                lock.release()

        return self._cache_objects[cache_class]

    def get_lock(self, cache_class: Type[Cache]) -> RLock:
        """
        Retrieve or create a lock object associated with the specified cache class.

        If a lock object associated with the specified cache class does not exist, a new RLock instance is created and returned.

        If the provided class is not a subclass of Cache, a warning is logged.

        :param cache_class: The class of the cache object associated with the lock.
        :return: The lock object associated with the specified cache class.
        """
        if not issubclass(cache_class, Cache):
            warning_msg = f"{cache_class} is not a subclass of Cache. Caching with this object may not work properly."
            logger.warning(warning_msg, Warning)
            return RLock()
            # Return a new RLock if the cache class is not a subclass of Cache

        with self._global_lock:
            if cache_class not in self._locks:
                self._locks[cache_class] = RLock()
            return self._locks[cache_class]

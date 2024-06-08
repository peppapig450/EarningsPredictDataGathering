from threading import RLock
from functools import wraps


class CacheRegistry:
    """Registry to store and retrieve decorated cache objects"""

    def __init__(self) -> None:
        self._cache_objects = {}
        self._locks = {}

    def cache_decorator(self, func):
        @wraps(func)
        def decorator(cache_class):
            def wrapper(*args, **kwargs):
                # Use the registry to get the decorated cache object
                decorated_func = self.get_cache(cache_class)
                # Call the decorated function with arguments
                return decorated_func(*args, **kwargs)

            return wrapper

        return decorator

    def get_cache(self, cache_class):
        with self.get_lock(cache_class):
            if cache_class not in self._cache_objects:
                cache_obj = cache_class()  # Create a new instance of the cache class
                decorated_func = self.cache_decorator(cache_obj)(cache_class)
                self._cache_objects[cache_class] = decorated_func
            return self._cache_objects[cache_class]

    def get_lock(self, cache_class):
        with self._locks.get(cache_class, RLock()):
            return self._locks[cache_class]

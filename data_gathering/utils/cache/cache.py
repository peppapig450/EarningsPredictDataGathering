import shelve
import os


class Cache:
    def __init__(self, cache_dir=None, filename="cache", writeback=True) -> None:
        self.cache_dir = cache_dir or os.path.join(self._get_root_directory(), ".cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.filepath = os.path.join(self.cache_dir, filename)

        self._cache = shelve.open(self.filepath, writeback=writeback)

    def __contains__(self, key):
        """Check if a key exists in the cache (without loading the value)"""
        return key in self._cache

    def __getitem__(self, key):
        """Get a value from the cache"""
        return self._cache[key]

    def __setitem__(self, key, value):
        """Set a value in the cache"""
        self._cache[key] = value

    def __delitem__(self, key):
        """Delete a value from the cache"""
        del self._cache[key]

    def close(self):
        """Close the cache file"""
        self._cache.close()

    def sync(self):
        """Write back cached entries to disk (if writeback is enabled)"""
        self._cache.sync()

    # TODO: maybe move to a utility file
    def _get_root_directory(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        root_dir = os.path.dirname(script_dir)
        return root_dir

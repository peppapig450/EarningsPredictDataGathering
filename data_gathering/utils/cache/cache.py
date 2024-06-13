import shelve
import os
from data_gathering.utils.file_utils import get_project_root_directory, create_path


class Cache:
    def __init__(
        self, cache_dir: os.PathLike | None = None, filename="cache", writeback=True
    ) -> None:
        self.cache_dir: os.PathLike = cache_dir or self._get_default_cache_directory()

        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(str(self.cache_dir))

        self.filepath = os.path.join(self.cache_dir, filename)

        # Open shelve for caching
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

    def _get_default_cache_directory(self) -> os.PathLike:
        """Use file_utils methods to get the default cache directory"""
        cache_path = create_path(
            ".cache",
            starting_path=get_project_root_directory(return_data_gathering=True),
            check_exists=False,
        )
        return cache_path

import pickle
import os

# shelve in the future if we need


class Cache:
    # future sqlite integration for actual caching
    def __init__(self, cache_dir=None, blacklist_symbols=None) -> None:
        self.cache_dir = cache_dir or self._get_root_directory()
        self.blacklist_symbols = blacklist_symbols

    def _get_root_directory(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        root_dir = os.path.dirname(script_dir)
        return root_dir

    def save_to_pickle(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load_from_pickle(cls, file_path):
        with open(file_path, "rb") as file:
            return pickle.load(file)

import pickle
import os

# shelve in the future if we need


class Cache:
    # future sqlite integration for actual caching
    def __init__(self, cache_dir=None, blacklist_symbols=None) -> None:
        self.cache_dir = cache_dir or os.path.join(self._get_root_directory(), ".cache")
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.blacklist_symbols = blacklist_symbols

    def _get_root_directory(self):
        script_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(script_path)
        root_dir = os.path.dirname(script_dir)
        return root_dir

    def save_to_pickle(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self, file)

    def load_from_pickle(self, file_path):
        with open(file_path, "rb") as file:
            data = pickle.load(file)
            return data

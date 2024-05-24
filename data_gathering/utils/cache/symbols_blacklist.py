from .cache import Cache
import pickle
import os


class BlacklistSymbolCache(Cache):
    def __init__(
        self, cache_dir=None, blacklist_symbols=None, pickle_file=None
    ) -> None:
        super().__init__(cache_dir=cache_dir)
        self.default_pickle_file = os.path.join(self.cache_dir, "blacklist.pkl")

        if pickle_file:
            self.load_blacklist_from_pickle(pickle_file)
        else:
            if not os.path.exists(self.default_pickle_file):
                self._create_default_blacklist()
            self.load_blacklist_from_pickle(self.default_pickle_file)
            if blacklist_symbols:
                self.blacklist = self.blacklist | frozenset(blacklist_symbols)
            self.new_symbols = set()

    def _create_default_blacklist(self):
        with open(self.default_pickle_file, "wb") as file:
            pickle.dump(frozenset(), file)

    def load_blacklist_from_pickle(self, file_path):
        with open(file_path, "rb") as file:
            self.blacklist = pickle.load(file)
        self.new_symbols = set()

    def save_blacklist_to_pickle(self, file_path):
        file_path = file_path or self.default_pickle_file
        with open(file_path, "wb") as file:
            new_blacklist = self.blacklist | self.new_symbols
            pickle.dump(new_blacklist, file)

    def is_blacklisted(self, symbol):
        return symbol in self.blacklist

    def add_symbol(self, symbol):
        if not self.is_blacklisted(symbol):
            self.new_symbols.add(symbol)

    def filter_blacklisted_symbols(self, symbols):
        """
        Takes a set of symbols and returns the set's difference with the blacklist.
        """
        return symbols - self.blacklist

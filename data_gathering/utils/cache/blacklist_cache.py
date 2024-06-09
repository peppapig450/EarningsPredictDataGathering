import shelve
import os
import importlib
from typing import override

from .cache import Cache


# XXX: ordered set?
class BlacklistSymbolCache(Cache):
    def __init__(self, cache_dir=None, pickle_file="blacklist.pkl") -> None:
        super().__init__(cache_dir)
        self._default_shelf_key = "blacklist"

        if self._default_shelf_key not in self._cache:
            self._initialize_blacklist_cache(pickle_file)

        self.load_blacklist_from_shelf()

        self._new_symbols = set()

    @override
    def __contains__(self, symbol):
        """Check if a symbol is in the blacklist, overriding the Cache __contains__"""
        return symbol in self.blacklist or symbol in self._new_symbols

    def _initialize_blacklist_cache(self, pickle_file):
        """Set the blacklist in the shelf to the old pickled cache version ensuring preservation of existing cache"""
        if pickle_file:
            old_pickle_blacklist = os.path.join(self.cache_dir, pickle_file)
            with open(old_pickle_blacklist, "rb") as file:
                pickle_module = importlib.import_module("pickle")
                blacklist = pickle_module.load(file)
                self._cache[self._default_shelf_key] = blacklist
        elif not os.path.exists(pickle_file):
            self._create_default_blacklist()

        super().sync()

    def _create_default_blacklist(self):
        """Create a default blacklist in the shelf cache."""
        self._cache[self._default_shelf_key] = set()
        super().sync()

    def load_blacklist_from_shelf(self):
        """Load the blacklist from the shelf cache."""
        self.blacklist = self._cache[self._default_shelf_key]

    def update_blacklist(self):
        """Merge the blacklist with any new symbols to blacklist and save"""
        # Combine frozenset with the new symbols to add and save
        updated_blacklist = self.blacklist | self._new_symbols

        self._cache[self._default_shelf_key] = updated_blacklist

    def blacklist_symbol(self, symbol):
        """Blacklist a symbol, adding it to the new_symbols set"""
        if symbol not in self:
            self._new_symbols.add(symbol)

    def filter_blacklisted_symbols(self, symbols):
        """
        Takes a set of symbols and returns the set's difference with the blacklist.
        """
        return symbols - self.blacklist

    @override
    def sync(self):
        """Overide the Cache class's sync to ensure that the blacklist is updated before closing."""
        self.update_blacklist()
        self._cache.sync()

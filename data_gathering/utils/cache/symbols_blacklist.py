from .cache import Cache


class BlacklistSymbolCache(Cache):
    def __init__(self, cache_dir=None, blacklist_symbols=None) -> None:
        super().__init__(cache_dir=cache_dir, blacklist_symbols=blacklist_symbols)
        self.blacklist = (
            frozenset(self.blacklist_symbols) if self.blacklist_symbols else frozenset()
        )
        self.new_symbols = set()

    def is_blacklisted(self, symbol):
        return symbol in self.blacklist

    def add_symbol(self, symbol):
        if not self.is_blacklisted(symbol):
            self.new_symbols.add(symbol)

    # TODO: load from pickle, concat the sets and write to pickle, implement in Symbol class and gather_all_data

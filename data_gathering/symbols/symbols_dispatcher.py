from collections import defaultdict
from ..upcoming_earnings import UpcomingEarning
from ..protocols import SymbolFilteringProtocol


class SymbolsDispatcher:
    filtered_symbols_cache: dict[str, list[UpcomingEarning]]

    def __init__(self):
        self.symbols: dict[str, list[UpcomingEarning]] = defaultdict(list)
        self.filtered_symbols_cache = {}

        # TODO: hold instance of Symbols Filter?

    def register_symbols(self, symbols_list: list[UpcomingEarning]):
        """Register the upcoming earning's symbols."""
        for earning in symbols_list:
            self.symbols[earning.currency].append(earning)

    def get_symbols(self, filter_protocol: SymbolFilteringProtocol):
        api_name = filter_protocol.get_api_name()

        # Check cache first
        if api_name in self.filtered_symbols_cache:
            return self.filtered_symbols_cache[api_name]

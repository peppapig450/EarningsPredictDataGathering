from collections import defaultdict
from ..upcoming_earnings import UpcomingEarning
from ..protocols import SymbolFilteringProtocol

class SymbolsDispatcher:
    def __init__(self):
        self.symbols: dict[str, list[UpcomingEarning]] = defaultdict(list)
        self.filtered_symbols_cache = dict[str, list[UpcomingEarning]]
        # TODO: hold instance of Symbols Filter?
        
    def register_symbols(self, symbols_list: list[UpcomingEarning]):
        """Register the upcoming earning's symbols."""
        for earning in symbols_list:
            self.symbols[earning.currency].append(earning)
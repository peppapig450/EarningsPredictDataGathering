from collections import defaultdict
from ..upcoming_earnings import UpcomingEarning
from ..protocols import SymbolFilteringProtocol
from .symbols_filter import SymbolsFilter

class SymbolsDispatcher:
    """
    A class to manage the registration and filtering of symbols according to API-specific protocols.

    Attributes:
    -----------
    symbols : defaultdict[str, list[UpcomingEarning]]
        A dictionary storing symbols organized by currency.
    filtered_symbols_cache : dict[str, dict[str, list[UpcomingEarning] | list[str]]]
        A cache to store filtered symbols for each API to avoid redundant filtering.
    filter : SymbolsFilter
        An instance of SymbolsFilter to handle the actual filtering logic.

    Methods:
    --------
    register_symbols(symbols_list: list[UpcomingEarning]) -> None
        Registers the upcoming earning's symbols.
    get_symbols(filter_protocol: SymbolFilteringProtocol) -> dict[str, list[UpcomingEarning] | list[str]]
        Retrieves and filters symbols according to the provided filtering protocol.
    """
    filtered_symbols_cache: dict[str, dict[str, list[UpcomingEarning] | list[str]]]

    def __init__(self):
        self.symbols: defaultdict[str, list[UpcomingEarning]] = defaultdict(list)
        self.filtered_symbols_cache = {}
        self.filter = SymbolsFilter()

    def register_symbols(self, symbols_list: list[UpcomingEarning]):
        """
        Registers the upcoming earning symbols.

        Args:
            symbols_list: A list of UpcomingEarning objects to be registered.
        """
        for earning in symbols_list:
            self.symbols[earning.currency].append(earning)

    def get_symbols(self, filter_protocol: SymbolFilteringProtocol):
        """
        Retrieves and filters symbols according to the provided filtering protocol.

        Args:
            filter_protocol: An instance of SymbolFilteringProtocol that defines the filtering criteria.

        Returns:
            A dictionary containing filtered symbols as dataclasses and their string representations.
        """
        api_name = filter_protocol.get_api_name()

        # Check cache first
        if api_name in self.filtered_symbols_cache:
            return self.filtered_symbols_cache[api_name]

        earnings_list, earnings_string_list = self.filter.get_filtered_symbols(filter_protocol, self.symbols)
        
        api_symbols: dict[str, list[UpcomingEarning] | list[str]] = {
            "as_dataclass": earnings_list,
            "as_str": earnings_string_list
        }
        
        self.filtered_symbols_cache[api_name] = api_symbols
        
        return api_symbols
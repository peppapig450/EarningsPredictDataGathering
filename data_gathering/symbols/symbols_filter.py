import re
from collections import defaultdict
from itertools import chain

from ..protocols import SymbolFilteringProtocol
from ..upcoming_earnings import UpcomingEarning

type SymbolsDict = defaultdict[str, list[UpcomingEarning]]

# TODO: add better error handling for edge cases
class SymbolsFilter:
    """
    A class to handle filtering of symbols according to specific API requirements.

    Attributes:
    -----------
    compiled_regex_patterns : dict[str, re.Pattern[str]]
        A dictionary storing compiled regular expression patterns for each API.

    Methods:
    --------
    _compile_regex(api_name: str, regex_pattern: str) -> re.Pattern[str]
        Compiles and stores the regex pattern for a given API if not already compiled.
    filter_symbol_by_regex(compiled_regex: re.Pattern[str], symbol: UpcomingEarning) -> bool | None
        Checks if a symbol matches the filter based on the provided compiled regex.
    filter_symbols_by_currency(valid_currencies: list[str], data: SymbolsDict) -> list[UpcomingEarning]
        Filters symbols based on valid currencies and returns a list of matching symbols.
    get_filtered_symbols(filter_protocol: SymbolFilteringProtocol, data: SymbolsDict) -> tuple[list[UpcomingEarning], list[str]]
        Filters symbols according to the protocol's rules and returns the filtered symbols and their strings.
    """
    compiled_regex_patterns: dict[str, re.Pattern[str]]

    def __init__(self) -> None:
        self.compiled_regex_patterns = {}

    def _compile_regex(self, api_name: str, regex_pattern: str):
        """
        Compiles and stores the regex pattern for a given API if not already compiled.

        Args:
            api_name: The name of the API for which the regex pattern is being compiled.
            regex_pattern: The regex pattern as a string.

        Returns:
            A compiled regular expression object.
        """
        if api_name not in self.compiled_regex_patterns:
            self.compiled_regex_patterns[api_name] = re.compile(regex_pattern)
        return self.compiled_regex_patterns[api_name]

    def filter_symbol_by_regex(
        self, compiled_regex: re.Pattern[str], symbol: UpcomingEarning
    ) -> bool:
        """
        Checks if a symbol matches the filter based on the provided compiled regex.

        Args:
            compiled_regex: A compiled regular expression object for filtering.
            symbol: The symbol to be checked against the filter.

        Returns:
            True if the symbol matches the filter, False otherwise.
        """
        if re.match(compiled_regex, symbol.symbol):
            return True
        return False

    def filter_symbols_by_currency(
        self, valid_currencies: list[str], data: SymbolsDict
    ):
        """
        Filters symbols based on valid currencies and returns a list of matching symbols.

        Args:
            valid_currencies: A list of valid currencies to filter symbols by.
            data: A dictionary of symbols organized by currency.

        Returns:
            A list of symbols that match the valid currencies.
        """
        #XXX: this can be simplified to a list comprehension if desired
        symbols: list[UpcomingEarning] = []

        for currency in valid_currencies:
            currency_symbols = data[currency]
            symbols.extend(currency_symbols)

        return symbols

    def get_filtered_symbols(
        self, filter_protocol: SymbolFilteringProtocol, data: SymbolsDict
    ):
        """
        Filters symbols according to the protocol's rules and returns the filtered symbols and their strings.

        Args:
            filter_protocol: An instance of SymbolFilteringProtocol that defines the filtering criteria.
            data: A dictionary of symbols organized by currency.

        Returns:
            A tuple containing a list of filtered symbols and a list of their symbol strings.
        """
        api_name = filter_protocol.get_api_name()
        regex_pat = filter_protocol.get_regex_pattern()
        valid_currencies = filter_protocol.get_valid_currencies()

        regex_pattern = self._compile_regex(api_name, regex_pat)

        filtered_symbols: list[UpcomingEarning] = []
        symbol_strings: list[str] = []

        # Make sure there's valid currencies specified by the protocol
        if not any(item == "" for item in valid_currencies):
            initial_symbols = self.filter_symbols_by_currency(valid_currencies, data)
        else:
            # If none specified use all the values
            initial_symbols = list(chain.from_iterable(data.values()))

        for earning in initial_symbols:
            if not self.filter_symbol_by_regex(regex_pattern, earning):
                filtered_symbols.append(earning)
                symbol_strings.append(earning.symbol)

        return filtered_symbols, symbol_strings

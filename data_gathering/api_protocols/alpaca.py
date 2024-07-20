from ..protocols import SymbolFilteringProtocol

class AlpacaSymbolsFilterProtocol(SymbolFilteringProtocol):
    def get_api_name(self) -> str:
        return "Alpaca"

    def get_valid_currencies(self) -> list[str]:
        return ["USD"]
    
    def get_regex_filter_pattern(self) -> str:
        return r"[-.]\S+$"
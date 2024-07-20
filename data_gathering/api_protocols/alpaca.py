"""
Module to hold any protocol implementation for Alpaca Api
"""

from typing import Protocol

from ..protocols import SymbolFilteringProtocol


class AlpacaSymbolsFilterProtocol(SymbolFilteringProtocol, Protocol):
    def get_api_name(self) -> str:
        return "Alpaca"

    def get_valid_currencies(self) -> list[str]:
        return ["USD"]
    
    def get_regex_filter_pattern(self) -> str:
        return r"[-.]\S+$"
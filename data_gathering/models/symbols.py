# models/symbol.py
import re


class Symbol:
    def __init__(self, symbol: str):
        self.symbol = symbol

    @classmethod
    def create(cls, symbol_str):
        return cls(symbol_str)

    @classmethod
    def filter_international_symbols(cls, symbols):
        return [symbol for symbol in symbols if not re.search("r\.[A-Z]*$", symbol)]

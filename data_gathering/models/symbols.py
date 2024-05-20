# models/symbol.py
import re


class Symbol:
    INTERNATIONAL_SYMBOL_PATTERN = r"\.[A-Z]*$"

    def __init__(self, symbol: str):
        self.symbol = symbol

    @classmethod
    def create(cls, symbol_str: str):
        if not re.match(cls.INTERNATIONAL_SYMBOL_PATTERN, symbol_str):
            return cls(symbol_str)

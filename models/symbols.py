# models/symbol.py

class Symbol:
    def __init__(self, symbol: str):
        self.symbol = symbol

    @classmethod
    def create(cls, symbol_str):
        return cls(symbol_str)

    @classmethod

# models/symbol.py
import re


class Symbol:
    """
    A class to represent a finacial instrument.

    Attributes:
        symbol (str): The symbol representing a finacial instrument.
    """

    INTERNATIONAL_SYMBOL_PATTERN = r"[-.][A-Z]+$"

    def __init__(self, symbol: str):
        """
        Initializes the Symbol instance with the provided symbol.

        Args:
            symbol (str): The symbol representing a financial instrument.
        """
        self.symbol: str = symbol

    def __str__(self) -> str:
        """
        Returns the symbol as a string representation of the Symbol instance.

        Returns:
            str: The symbol as a string.
        """
        return self.symbol

    @classmethod
    def create(cls, symbol_str: str) -> "Symbol":
        """
        Creates a Symbol instance if the provided string isn't on an international exchange.

        Args:
            symbol_str (str): The string to be evaluated and potentially converted into a Symbol instance.

        Returns:
            Symbol: An instance of the Symbol class if the string does not match the international symbol pattern.
            None: If the string matches the international symbol pattern.
        """
        if not re.search(cls.INTERNATIONAL_SYMBOL_PATTERN, symbol_str):
            return cls(symbol_str)
        return None

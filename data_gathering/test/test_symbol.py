# tests/test_symbol.py
import pytest
from data_gathering.models.symbols import Symbol


def test_symbol_initialization():
    # Test that a Symbol instance is initialized correctly
    sym = Symbol("AAPL")
    assert sym.symbol == "AAPL"


def test_create_valid_symbol():
    # Test creating a Symbol instance with a valid symbol string
    sym = Symbol.create("AAPL")
    assert sym is not None
    assert sym.symbol == "AAPL"

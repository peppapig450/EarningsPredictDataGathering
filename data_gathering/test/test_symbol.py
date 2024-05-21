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


def test_create_invalid_symbol():
    # Test that None is returned for an international symbol string
    sym = Symbol.create("KONT.ST")
    assert sym is None


def test_create_empty_string():
    # Test creating a Symbol instance with an empty string
    sym = Symbol.create("")
    assert sym is not None
    assert sym.symbol == ""


def test_create_non_matching_symbol():
    # Test creating a Symbol instance with a non-matching symbol string
    sym = Symbol.create("12345")
    assert sym is not None
    assert sym.symbol == "12345"


@pytest.mark.parametrize(
    "symbol_str, expected",
    [
        ("AAPL", True),
        ("AAPL.TL", False),
        ("010XY", True),
        ("010XY.CN", False),
        ("BDP-EQ", False),
        ("", True),
    ],
)
def test_create_parameterized(symbol_str, expected):
    # Parameterized test for multiple cases
    sym = Symbol.create(symbol_str)
    if expected:
        assert sym is not None
        assert sym.symbol == symbol_str
    else:
        assert sym is None

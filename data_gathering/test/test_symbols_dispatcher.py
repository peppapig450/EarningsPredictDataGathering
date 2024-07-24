import re
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from ..models.date_range import DateTuple
from ..protocols.symbol_filtering import SymbolFilteringProtocol
from ..symbols import SymbolsDispatcher, SymbolsFilter
from ..upcoming_earnings.upcoming_earning import UpcomingEarning


class SymbolsDistributionTest:
    @pytest.fixture
    def filter_protocol(self):
        filter_protocol = MagicMock(SymbolFilteringProtocol)
        filter_protocol.get_api_name.return_value = "test_api"
        filter_protocol.get_regex_pattern.return_value = r"INVALID"
        filter_protocol.get_valid_currencies.return_value = ["USD"]
        return filter_protocol

    @pytest.fixture
    def valid_upcoming_earning(self):
        return UpcomingEarning(
            symbol="AAPL",
            company_name="Apple Inc.",
            report_date=DateTuple(datetime(2024, 7, 31), "2024-07-31"),
            fiscal_year_end=DateTuple(datetime(2024, 9, 30), "2024-09-30"),
            currency="USD",
        )

    @pytest.fixture
    def upcoming_earnings(self):
        return [
            UpcomingEarning(
                symbol="AAPL",
                company_name="Apple Inc.",
                report_date=DateTuple(datetime(2024, 7, 31), "2024-07-31"),
                fiscal_year_end=DateTuple(datetime(2024, 9, 30), "2024-09-30"),
                currency="USD",
            ),
            UpcomingEarning(
                symbol="INVALID",
                company_name="INVALID",
                report_date="2024-08-04",
                fiscal_year_end="2025-05-29",
                currency="USD",
            ),
        ]


class TestSymbolsDispatcher(SymbolsDistributionTest):
    @pytest.fixture
    def symbols_dispatcher(self):
        return SymbolsDispatcher()

    def test_register_symbols(self, symbols_dispatcher, upcoming_earnings):
        symbols_dispatcher.register_symbols(upcoming_earnings)
        assert symbols_dispatcher.symbols["USD"] == upcoming_earnings

    def test_get_symbols_cache(
        self, symbols_dispatcher, upcoming_earnings, filter_protocol
    ):
        symbols_dispatcher.register_symbols(upcoming_earnings)

        # First call, should filter and cache
        result = symbols_dispatcher.get_symbols(filter_protocol)
        assert "dataclass" in result
        assert "strings" in result

        # Second call, should use cache
        result = symbols_dispatcher.get_symbols(filter_protocol)
        assert result["dataclass"] == [upcoming_earnings[0]]
        assert result["strings"] == ["AAPL"]

    def test_get_symbols_no_cache(
        self, symbols_dispatcher, upcoming_earnings, filter_protocol
    ):
        symbols_dispatcher.register_symbols(upcoming_earnings)

        result = symbols_dispatcher.get_symbols(filter_protocol)

        assert "dataclass" in result
        assert "strings" in result
        assert result["dataclass"] == [upcoming_earnings[0]]
        assert result["strings"] == ["AAPL"]


class TestSymbolsFilter(SymbolsDistributionTest):
    @pytest.fixture
    def symbols_filter(self):
        return SymbolsFilter()

    def test_compile_regex(self, symbols_filter):
        api_name = "test_api"
        regex_pattern = r"AAPL"
        compiled_regex = symbols_filter._compile_regex(api_name, regex_pattern)

        assert isinstance(compiled_regex, re.Pattern)
        assert symbols_filter.compiled_regex_patterns[api_name] == compiled_regex

    def test_filter_symbol_by_regex(self, symbols_filter, valid_upcoming_earning):
        regex_pattern = r"AAPL"
        compiled_regex = symbols_filter._compile_regex("test_api", regex_pattern)

        result = symbols_filter.filter_symbol_by_regex(
            compiled_regex, valid_upcoming_earning
        )
        assert result is True

        # TODO: filter should be false to not exclude

    def test_filter_symbols_by_currency(self, symbols_filter, valid_upcoming_earning):
        data = {"USD": [valid_upcoming_earning], "EUR": []}
        valid_currencies = ["USD"]

        result = symbols_filter.filter_symbols_by_currency(valid_currencies, data)
        assert result == [valid_upcoming_earning]

    def test_get_filtered_symbols(
        self, symbols_filter, valid_upcoming_earning, filter_protocol
    ):
        data = {"USD": [valid_upcoming_earning], "EUR": []}

        filtered_symbols, symbol_strings = symbols_filter.get_filtered_symbols(
            filter_protocol, data
        )

        assert len(filtered_symbols) == 1
        assert filtered_symbols[0] == valid_upcoming_earning
        assert symbol_strings == ["AAPL"]

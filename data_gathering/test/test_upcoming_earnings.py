from datetime import date
import pytest
import requests
from requests.models import Response
from pydantic import ValidationError

from data_gathering.data.get_upcoming_earnings import (
    NoUpcomingEarningsError,
    UpcomingEarnings,
)
from data_gathering.models.upcoming_earning import UpcomingEarning
from data_gathering.utils.cache.symbols_blacklist import BlacklistSymbolCache
from data_gathering.config.api_keys import APIKeys


# Mocking the APIKeys class
class MockAPiKeys:
    fmp_api_key = "test_api_key"


@pytest.fixture
def mock_api_keys():
    return MockAPiKeys()


@pytest.fixture
def mock_cache(mocker) -> BlacklistSymbolCache:
    cache = mocker.Mock(spec=BlacklistSymbolCache)
    cache.is_blacklisted.side_effect = lambda symbol: symbol in ["BLACKLISTED"]
    return cache


@pytest.fixture
def mock_response(mocker):
    def _mock_response(json_data, status_code):
        mock_resp = mocker.Mock(spec=Response)
        mock_resp.json.return_value = json_data
        mock_resp.status_code = mocker.Mock()
        if status_code != 200:
            mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError()
        return mock_resp

    return _mock_response


def test_get_upcoming_symbols_list_success(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = [
        {"symbol": "AAPL", "date": "2024-06-01"},
        {"symbol": "GOOGL", "date": "2024-06-02"},
    ]
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)
    earnings_list = upcoming_earnings.get_upcoming_earnings_list(
        "2024-06-01", "2024-06-30"
    )

    assert len(earnings_list) == 2
    assert earnings_list[0].symbol == "AAPL"
    assert earnings_list[0].date == date(2024, 6, 1)
    assert earnings_list[1].symbol == "GOOGL"
    assert earnings_list[1].date == date(2024, 6, 2)


def test_get_upcoming_earnings_list_no_data(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = []
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)

    with pytest.raises(RuntimeError):
        upcoming_earnings.get_upcoming_earnings_list("2024-06-01", "2024-06-30")


def test_get_upcoming_earnings_list_validation_error(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = [{"symbol": "AAPL", "date": "invalid-date"}]
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)

    with pytest.raises(RuntimeError):
        upcoming_earnings.get_upcoming_earnings_list("2024-06-01", "2024-06-30")


def test_get_upcoming_earnings_list_request_exception(
    mocker, mock_api_keys, mock_cache
):
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException)

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)

    with pytest.raises(RuntimeError):
        upcoming_earnings.get_upcoming_earnings_list("2024-06-01", "2024-06-30")


def test_get_upcoming_earnings_list_strings_success(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = [
        {"symbol": "AAPL", "date": "2024-06-01"},
        {"symbol": "GOOGL", "date": "2024-06-02"},
    ]
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)
    earnings_list_strings = upcoming_earnings.get_upcoming_earnings_list_strings(
        "2024-06-01", "2024-06-30"
    )

    assert len(earnings_list_strings) == 2
    assert earnings_list_strings == ["AAPL", "GOOGL"]


def test_get_upcoming_earnings_list_excludes_invalid_symbols(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = [
        {"symbol": "AAPL", "date": "2024-06-01"},
        {"symbol": "GOOGL", "date": "2024-06-02"},
        {"symbol": "AAPL-OE", "date": "2024-06-03"},
        {"symbol": "AAPL.LI", "date": "2024-06-04"},
    ]
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)
    earnings_list = upcoming_earnings.get_upcoming_earnings_list(
        "2024-06-01", "2024-06-30"
    )

    assert len(earnings_list) == 2
    assert earnings_list[0].symbol == "AAPL"
    assert earnings_list[0].date == date(2024, 6, 1)
    assert earnings_list[1].symbol == "GOOGL"
    assert earnings_list[1].date == date(2024, 6, 2)


def test_get_upcoming_earnings_list_excludes_blacklisted_symbols(
    mocker, mock_api_keys, mock_cache, mock_response
):
    mock_data = [
        {"symbol": "AAPL", "date": "2024-06-01"},
        {"symbol": "GOOGL", "date": "2024-06-02"},
        {"symbol": "BLACKLISTED", "date": "2024-06-03"},
    ]
    mock_cache.is_blacklisted.side_effect = lambda symbol: symbol == "BLACKLISTED"
    mocker.patch("requests.get", return_value=mock_response(mock_data, 200))

    upcoming_earnings = UpcomingEarnings(api_keys=mock_api_keys, cache=mock_cache)
    earnings_list = upcoming_earnings.get_upcoming_earnings_list(
        "2024-06-01", "2024-06-30"
    )

    assert len(earnings_list) == 2
    assert earnings_list[0].symbol == "AAPL"
    assert earnings_list[0].date == date(2024, 6, 1)
    assert earnings_list[1].symbol == "GOOGL"
    assert earnings_list[1].date == date(2024, 6, 2)

from datetime import date
import pytest
import requests
from requests.models import Response
from pydantic import ValidationError

from data_gathering.data.get_upcoming_earnings import UpcomingEarning, NoUpcomingEarningsError, UpcomingEarnings
from data_gathering.utils.cache.cache_registry import CacheRegistry
from data_gathering.utils.cache.blacklist_cache import BlacklistSymbolCache
from data_gathering.config.api_keys import APIKeys, APIService


class MockAPiKeys(APIKeys):
    _keys = {APIService.FMP: "test_api_key"}


@pytest.fixture
def mock_api_keys():
    return MockAPiKeys()

@pytest.fixture
def mock_cache_registry(mocker):
    return mocker.MagicMock(spec=CacheRegistry)

@pytest.fixture
def upcoming_earnings_instance(mock_api_keys, mock_cache_registry):
    return UpcomingEarnings(mock_api_keys, mock_cache_registry)

def test_get_upcoming_earnings_list_valid_response(upcoming_earnings_instance, mocker):
    # Mocking requests.get and response
    mock_get = mocker.patch("requests.get")
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"symbol": "AAPL", "date": "2024-06-12"},
        {"symbol": "GOOGL", "date": "2024-06-13"}
    ]
    mock_get.return_value = mock_response
    
    # Mock cache decorator to return the method itself without applying caching logic
    mock_cache_decorator = mocker.patch.object(upcoming_earnings_instance.cache_registry, 'cache_decorator')
    mock_cache_decorator.side_effect = lambda func: func
    
    # Call the method under test
    earnings_list = upcoming_earnings_instance.get_upcoming_earnings_list("2024-06-10", "2024-06-15")
    
    # Assert that the method returns a list of upcoming earnings
    assert isinstance(earnings_list, list)
    assert len(earnings_list) == 2
    assert all(isinstance(earning, UpcomingEarning) for earning in earnings_list)
    
def test_get_upcoming_earnings_list_no_data(upcoming_earnings_instance, mocker):
    # Mocking requests.get and response
    mock_get = mocker.patch("requests.get")
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [] # Simulating empty response
    mock_get.return_value = mock_response
    
    # Mock cache to return an empty list
    mock_cache = mocker.MagicMock(spec=BlacklistSymbolCache)
    mock_cache.__contains__.side_effect = lambda symbol: False  # Mocking no blacklisted symbols
    upcoming_earnings_instance.cache_registry.get_cache.return_value = mock_cache 
    
    # Call the method under test
    with pytest.raises(NoUpcomingEarningsError):
        upcoming_earnings_instance.get_upcoming_earnings_list("2024-06-10", "2024-06-15")


def test_get_upcoming_earnings_list_blacklisted_symbols(upcoming_earnings_instance, mocker):
    # Mocking requests.get and response
    mock_get = mocker.patch('requests.get')
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"symbol": "AAPL", "date": "2024-06-12"},
        {"symbol": "GOOGL", "date": "2024-06-13"},
        {"symbol": "INVALID!", "date": "2024-06-14"}
    ]
    mock_get.return_value = mock_response

    # Mock cache to return a list containing one blacklisted symbol
    mock_cache = mocker.MagicMock(spec=BlacklistSymbolCache)
    mock_cache.__contains__.side_effect = lambda symbol: symbol == "INVALID!"  # Mocking "INVALID!" symbol is blacklisted
    upcoming_earnings_instance.cache_registry.get_cache.return_value = mock_cache

    # Call the method under test
    earnings_list = upcoming_earnings_instance.get_upcoming_earnings_list("2024-06-10", "2024-06-15")

    assert isinstance(earnings_list, list)
    assert len(earnings_list) == 2
    assert all(isinstance(earning, UpcomingEarning) for earning in earnings_list)
    assert all(earning.symbol != "INVALID!" for earning in earnings_list)  # Ensure "INVALID!" symbol is not present

def test_get_upcoming_earnings_list_validation_error(upcoming_earnings_instance, mocker):
    # Mocking grequests.get and response
    pass
    # TODO: figrure how to check chained eceptions


def test_get_upcoming_earnings_list_request_exception(
    mocker, mock_api_keys, mock_cache
):
    pass
    #TODO:


def test_get_upcoming_earnings_list_strings_success(
    mocker, mock_api_keys, mock_cache, mock_response
):
    pass
    #TODO:

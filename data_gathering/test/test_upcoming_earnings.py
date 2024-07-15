from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from csv import Error as CsvError
from requests.exceptions import HTTPError

# Mocking DateTuple and UpcomingEarningCreationError for self-contained testing
from ..models.date_range import DateTuple
from ..exceptions import UpcomingEarningCreationError, NoUpcomingEarningsError
from ..upcoming_earnings import UpcomingEarning, UpcomingEarningsGatherer

# Mocked DateTuple class
class MockDateTuple(DateTuple):
    def __new__(cls, date, date_str):
        return super().__new__(cls, date, date_str)

# Test data
valid_data = {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "reportDate": "2024-07-31",
    "fiscalDateEnding": "2024-09-30",
    "currency": "USD",
}

invalid_data_missing_keys = {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    # Missing "reportDate"
    "fiscalDateEnding": "2024-09-30",
    "currency": "USD",
}


@pytest.fixture
def valid_upcoming_earning():
    return UpcomingEarning(
        symbol="AAPL",
        company_name="Apple Inc.",
        report_date=DateTuple(datetime(2024, 7, 31), "2024-07-31"),
        fiscal_year_end=DateTuple(datetime(2024, 9, 30), "2024-09-30"),
        currency="USD"
    )
    
@pytest.fixture
def mock_api_keys():
    return MagicMock()

@pytest.fixture
def mock_response():
    return MagicMock()

@pytest.fixture
def mock_requests_get(monkeypatch, mock_response):
    def mock_get(*args, **kwargs):
        return mock_response
    
    monkeypatch.setattr('requests.get', mock_get)

@pytest.fixture
def mock_logger(monkeypatch):
    mock_logger_instance = MagicMock()
    mock_get_logger = MagicMock(return_value=mock_logger_instance)
    monkeypatch.setattr('logging.getLogger', mock_get_logger)
    return mock_logger_instance

@pytest.fixture
def upcoming_earnings_gatherer(mock_api_keys, mock_logger):
    return UpcomingEarningsGatherer(mock_api_keys)

def test_upcoming_earning_from_dict_success(valid_upcoming_earning):
    instance = UpcomingEarning.from_dict(valid_data)
    assert instance.symbol == "AAPL"
    assert instance.company_name == "Apple Inc."
    assert instance.report_date.date == datetime(2024, 7, 31)
    assert instance.report_date.date_str == "2024-07-31"
    assert instance.fiscal_year_end.date == datetime(2024, 9, 30)
    assert instance.fiscal_year_end.date_str == "2024-09-30"
    assert instance.currency == "USD"

def test_upcoming_earning_from_dict_missing_keys():
    with pytest.raises(UpcomingEarningCreationError):
        UpcomingEarning.from_dict(invalid_data_missing_keys)

def test_upcoming_earning_create_date_tuple(valid_upcoming_earning):
    date_value = "2024-07-31"
    date_format = "%Y-%m-%d"
    result = valid_upcoming_earning._create_date_tuple(date_value, date_format)
    assert isinstance(result, DateTuple)
    assert result.date == datetime.strptime(date_value, date_format)
    assert result.date_str == date_value

def test_upcoming_earning_post_init(valid_upcoming_earning):
    assert valid_upcoming_earning.report_date.date == datetime(2024, 7, 31)
    assert valid_upcoming_earning.report_date.date_str == "2024-07-31"
    assert valid_upcoming_earning.fiscal_year_end.date == datetime(2024, 9, 30)
    assert valid_upcoming_earning.fiscal_year_end.date_str == "2024-09-30"

def test_upcoming_earning_str(valid_upcoming_earning):
    assert str(valid_upcoming_earning) == "AAPL"
    
def test_get_upcoming_earnings_list_success(upcoming_earnings_gatherer, mock_requests_get, mock_response):
    # Mock response data
    mock_response.text = "symbol,name,reportDate,fiscalDateEnding,currency\nAAPL,Apple Inc.,2024-07-31,2024-09-30,USD\n"

    # Mock UpcomingEarning.from_dict()
    mock_earning_instance = MagicMock(spec=UpcomingEarning)
    with patch.object(UpcomingEarning, 'from_dict', return_value=mock_earning_instance) as mock_from_dict:
        # Test function
        earnings_list = upcoming_earnings_gatherer.get_upcoming_earnings_list('2024-08-01')

        # Assertions
        assert len(earnings_list) == 1
        assert earnings_list[0] == mock_earning_instance
        mock_from_dict.assert_called_once()

def test_get_upcoming_earnings_list_empty_response(upcoming_earnings_gatherer, mock_requests_get, mock_response, mock_logger):
    # Mock empty response
    mock_response.text = ""

    # Test function
    with pytest.raises(NoUpcomingEarningsError):
        upcoming_earnings_gatherer.get_upcoming_earnings_list('2024-08-01')

    # Check logging
    mock_logger.critical.assert_called_once_with('No upcoming earnings found: upcoming_earnings_list is empty', exc_info=True, stack_info=True)

def test_get_upcoming_earnings_list_http_error(upcoming_earnings_gatherer, mock_response, mock_logger):
    # Mock HTTPError
    mock_response.raise_for_status.side_effect = HTTPError()
    
    # Test function
    with pytest.raises(NoUpcomingEarningsError):
        upcoming_earnings_gatherer.get_upcoming_earnings_list('2024-08-01')

    # Check logging
    mock_logger.critical.assert_called_once_with('HTTP error occurred while retrieving upcoming earnings list: ', exc_info=True, stack_info=True)

def test_get_upcoming_earnings_list_csv_error(upcoming_earnings_gatherer, mock_requests_get, mock_response, mock_logger):
    # Mock CSVError
    mock_response.text = "invalid,csv,data"
    mock_response.raise_for_status.side_effect = CsvError()

    # Test function
    with pytest.raises(NoUpcomingEarningsError):
        upcoming_earnings_gatherer.get_upcoming_earnings_list('2024-08-01')

    # Check logging
    mock_logger.critical.assert_called_once_with('CSV parsing error occurred while retrieving upcoming earnings list: ', exc_info=True, stack_info=True)
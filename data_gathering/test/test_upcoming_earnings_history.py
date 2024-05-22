import pytest
import aiohttp
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime
from data_gathering.config.api_keys import APIKeys
from data_gathering.data.historical_prices.upcoming_earnings_history import (
    HistoricalData,
)


@pytest.fixture
def api_keys():
    return APIKeys(
        apca_key_id="test_key_id",
        apca_api_secret_key="test_secret_key",
        fmp_api_key=None,
        finnhub_api_key=None,
        alpha_vantage_api_key=None,
    )


@pytest.fixture
def data_fetcher():
    class DataFetcher:
        semaphore = asyncio.Semaphore(10)

    return DataFetcher()


@pytest.fixture
async def historical_data(api_keys, data_fetcher):
    hd = HistoricalData(api_keys, "2023-01-01", "2023-01-01", data_fetcher)
    yield hd
    await hd.close()


@pytest.mark.asyncio
async def test_fetch_historical(historical_data):
    symbol = "AAPL"

    mock_response = {
        "bars": [
            {
                "c": 150.0,
                "h": 155.0,
                "l": 145.0,
                "n": 10000,
                "o": 148.0,
                "t": "2023-01-01T00:00:00Z",
                "v": 20000,
                "vw": 151.0,
            }
        ]
    }

    with patch("aiohttp.ClientSession.get", new=AsyncMock()) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        data = await historical_data.fetch_historical_data(symbol)
        assert data is not None
        assert symbol in historical_data.historical_data_by_symbol
        df = historical_data.historical_data_by_symbol[symbol]
        assert not df.empty
        assert df.index[0] == datetime(2023, 1, 1)


@pytest.mark.asyncio
async def test_fetch_historical_data_no_bars(historical_data):
    symbol = "AAPL"

    mock_response = {"bars": []}

    with patch("aiohttp.ClientSession.get", new=AsyncMock()) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )

        data = await historical_data.fetch_historical_data(symbol)
        assert data is not None
        assert symbol in historical_data.symbols_without_historical_data


@pytest.mark.asyncio
async def test_fetch_historical_data_with_error(historical_data):
    symbol = "AAPL"

    with patch("aiohttp.ClientSession.get", new=AsyncMock()) as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"error": "some error"}
        )

        data = await historical_data.fetch_historical_data(symbol)
        assert data is None
        assert symbol in historical_data.symbols_without_historical_data


@pytest.mark.asyncio
async def test_cache_load_and_save(historical_data):
    historical_data.symbols_without_historical_data = {"AAPL", "MSFT"}
    historical_data.save_cache_to_file()

    loaded_cache = historical_data.load_cache_from_file()
    assert loaded_cache == {"AAPL", "MSFT"}

import pytest
from unittest.mock import MagicMock, patch
from data_gathering.data.historical.historical_data_session import (
    HistoricalDataSessionManager,
)
from data_gathering.config.api_keys import APIKeys, APIService


class MockAPIKeys(APIKeys):
    def get_key(self, service):
        return "mock_id", "mock_secret_key"


@pytest.fixture
def api_keys():
    return MockAPIKeys()


@pytest.mark.asyncio
async def test_manage_session(api_keys):
    manager = HistoricalDataSessionManager(api_keys)
    async with manager.manage_session() as session:
        assert session is not None


@pytest.mark.asyncio
async def test_get_base_url(api_keys):
    manager = HistoricalDataSessionManager(api_keys)
    assert manager.get_base_url() == "https://data.alpaca.markets/"


@pytest.mark.asyncio
async def test_get_headers(api_keys):
    manager = HistoricalDataSessionManager(api_keys)
    headers = manager.get_headers()
    assert headers == {
        "APCA-API-KEY-ID": "mock_id",
        "APCA-API-SECRET-KEY": "mock_secret_key",
    }


@pytest.mark.asyncio
async def test_session_closed_after_context_exit(api_keys):
    manager = HistoricalDataSessionManager(api_keys)
    async with manager.manage_session() as session:
        assert not session.closed
    assert session.closed

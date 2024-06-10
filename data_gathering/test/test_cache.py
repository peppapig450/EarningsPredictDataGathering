import os
import pytest
import shelve
from data_gathering.utils.cache.cache import Cache
from data_gathering.utils.cache.blacklist_cache import BlacklistSymbolCache
from data_gathering.utils.cache.cache_registry import CacheRegistry


# Fixture to provide a temporary directory for cache testing
@pytest.fixture
def temp_cache_dir(tmpdir):
    return tmpdir.mkdir("cache")


# Fixture to provide a CacheRegistry instance for testing
@pytest.fixture
def cache_registry():
    return CacheRegistry()


# Fixture to provide a BlackListSymbolCache instance for testing
@pytest.fixture
def blacklist_cache(temp_cache_dir):
    return BlacklistSymbolCache(cache_dir=temp_cache_dir)


# Test case for Cache class
def test_cache(temp_cache_dir):
    cache = Cache(cache_dir=temp_cache_dir)
    key = "test_key"
    value = "test_value"

    # Test cache set and get functionality
    cache[key] = value
    assert cache[key] == value

    # Test cache contains functionality
    assert key in cache

    # Test cache delete functionality
    del cache[key]
    assert key not in cache

    cache.close()


# Test case for CacheRegistry class
def test_cache_registry(cache_registry, mocker):
    # Mock cache for testing
    class MockCache(Cache):
        def __init__(self, cache_dir=None):
            super().__init__(cache_dir)
            self._cache = mocker.Mock()

        def sync(self):
            pass

        def close(self):
            pass

    mock_cache_class = MockCache

    # Test get_cache method
    cache = cache_registry.get_cache(mock_cache_class)
    assert isinstance(cache, MockCache)


# Test case for BlacklistSymbolCache
def test_blacklisted_symbol_cache(blacklist_cache):
    symbol = "test_symbol"

    # Test blacklist_symbol method
    blacklist_cache.blacklist_symbol(symbol)
    assert symbol in blacklist_cache

    # Test filter_blacklisted method
    symbols = {"test_symbol1", "test_symbol2", "test_symbol3"}
    filtered_symbols = blacklist_cache.filter_blacklisted_symbols(symbols)
    assert symbol not in filtered_symbols

    # Test update_blacklist method
    blacklist_cache.update_blacklist()
    assert symbol in blacklist_cache.blacklist

    blacklist_cache.close()


# Test case for CacheRegistry's cache_decorator
def test_cache_decorator(cache_registry, temp_cache_dir, mocker):
    class MockCache(Cache):
        def __init__(self):
            super().__init__()
            self._cache = mocker.Mock()

        def sync(self):
            pass

        def close(self):
            pass

    mock_cache_class = MockCache

    @cache_registry.cache_decorator(MockCache)
    def decorated_func(cache, arg1, arg2):
        return cache, arg1, arg2

    (
        cache,
        arg1,
        arg2,
    ) = decorated_func("arg_value1", "arg2_value")

    assert isinstance(cache, MockCache)
    assert arg1 == "arg1_value"
    assert arg2 == "arg2_value"

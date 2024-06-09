import os
import pytest
import shelve
from data_gathering.utils.cache.cache import Cache


@pytest.fixture
def fake_cache_file(tmp_path):
    """
    Fixture to create a fake cache file for testing purposes.

    Args:
    - tmp_path: Built-in pytest fixture that provides a temporary directory unique to the test invocation.

    Yields:
    - The path to the fake cache file.
    """
    # Setup: Create a temporary directory and fake cache file
    cache_dir = tmp_path / ".cache"
    cache_dir.mkdir()
    cache_file = cache_dir / "cache.db"

    # Initialize the cache with some fake data
    with shelve.open(str(cache_file)) as fake_cache:
        fake_cache["test_key"] = "test_value"

    yield cache_file  # Yield the path to the fake cache file to the test function

    # Teardown: The temporary directory and files are automatically cleaned up by pytest


@pytest.fixture
def cache(fake_cache_file):
    """
    Fixture to create a Cache object using the fake cache file.

    Args:
    - fake_cache_file: Path to the fake cache file provided by the `fake_cache_file` fixture.

    Yields:
    - Cache object initialized with the fake cache file.
    """
    # Initialize the Cache object with the fake cache file
    cache = Cache(
        cache_dir=os.path.basename(fake_cache_file),
        filename=os.path.basename(fake_cache_file),
    )
    yield cache  # Yield the Cache object to the test function
    cache.close()

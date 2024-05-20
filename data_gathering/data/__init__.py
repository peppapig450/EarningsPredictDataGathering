from .gather_all_data import DataFetcher


async def fetch_all_data():
    # Create an instance of DataFetcher within the function
    data_fetcher = DataFetcher()
    await data_fetcher.fetch_all_data()


__all__ = ["fetch_all_data"]

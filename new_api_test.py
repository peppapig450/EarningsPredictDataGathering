import requests
import csv
from data_gathering.config import APIKeys
from data_gathering.config.api_keys import APIService
from urllib.parse import urlencode
import pandas as pd
from pprint import pprint
import io
import timeit


def build_earnings_calendar_url(api_key, month: int = 3):
    """
    This function builds the URL for the Alpha Vantage Earnings Calendar API using urllib.parse.

    Args:
        month: An integer representing the month (1-12).
        api_key: Your Alpha Vantage API key.

    Returns:
        A string containing the complete URL for the API request.
    """
    BASE_URL = "https://www.alphavantage.co/query"
    # Early exit if the inputted month is incorrect
    if month not in (3, 6, 12):
        raise ValueError("Invalid month argument passed. Use 3, 6, or 12.")

    params = {
        "function": "EARNINGS_CALENDAR",
        "horizon": f"{month}month",
        "apikey": api_key,
    }

    # Encode parameters for url construction
    encoded_params = urlencode(params)
    url = f"{BASE_URL}?{encoded_params}"
    return url


def make_api_request(url):
    """
    This function fetches CSV data from an API and parses it using pandas.

    Args:
        url: The URL of the API endpoint returning CSV data.

    Returns:
        A pandas DataFrame object representing the CSV data.
    """

    with requests.Session() as s:
        response = s.get(url)
        if response.status_code == 200:
            # Read csv data
            data_string = response.content.decode("utf-8")
            df = pd.read_csv(io.StringIO(data_string))
            return df
        raise Exception(f"API request failed with status code: {response.status_code}")


def make_api_request_csv(url):
    with requests.Session() as s:
        response = s.get(url)
        if response.status_code == 200:
            reader = csv.DictReader(response.text.splitlines(), dialect="unix")
            data = list(reader)
            return data
        raise Exception(f"API request failed with status code: {response.status_code}")


def benchmark_csv_parsing(url, method):
    """
    This function benchmarks the time taken to parse CSV data using the specified method.

    Args:
        url: The URL of the API endpoint returning CSV data.
        method: A string indicating the parsing method ('pandas' or 'csv').

    Returns:
        A float representing the execution time in seconds.
    """
    if method == "pandas":
        stmt = """make_api_request(url)"""
    elif method == "csv":
        stmt = """make_api_request_csv(url)"""
    else:
        raise ValueError("Invalid parsing method specified.")
    return timeit.timeit(stmt, number=5)


if __name__ == "__main__":
    api_keys = APIKeys()
    alpha_vantage_key = api_keys.get_key(APIService.ALPHA_VANTAGE)
    url = build_earnings_calendar_url(alpha_vantage_key, 12)
    # Benchmarking using timeit
    pandas_time = benchmark_csv_parsing(url, "pandas")
    csv_time = benchmark_csv_parsing(url, "csv")

    # Print results
    print(f"Average execution time for pandas: {pandas_time:.4f} seconds")
    print(f"Average execution time for csv: {csv_time:.4f} seconds")

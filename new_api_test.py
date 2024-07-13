import requests
import csv
from data_gathering.config import APIKeys
from data_gathering.config.api_keys import APIService
from urllib.parse import urlencode
import pandas as pd
import io

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
        "apikey": api_key
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
        
        
if __name__ == "__main__":    
    api_keys = APIKeys()
    alpha_vantage_key = api_keys.get_key(APIService.ALPHA_VANTAGE)
    url = build_earnings_calendar_url(alpha_vantage_key, 12)
    df = make_api_request(url)
    print(df.head())
    print(df)
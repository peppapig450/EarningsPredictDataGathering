import requests
import fmpsdk
import pandas as pd
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import fmp_api_key, apca_api_secret_key, apca_key_id

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": apca_key_id,
    "APCA-API-SECRET-KEY": apca_api_secret_key,
}


def fetch_data(url_parts, symbol):

    base_url, rest_of_link = url_parts
    url = f"{base_url}?symbols={symbol}{rest_of_link}"
    response = requests.get(url, headers=headers)

    data = response.json()

    try:
        return data["bars"]
    except KeyError:
        return None


def get_upcoming_earnings(api_key, from_date, to_date):
    earnings_data = fmpsdk.earning_calendar(
        apikey=fmp_api_key, from_date=from_date, to_date=to_date
    )

    filtered_symbols = []
    for earning in earnings_data:
        symbol = earning.get("symbol")
        # Filter if symbol exists, is a string, and doesn't end with country code extension
        if symbol and not re.search(r"\.[A-Z]*$", symbol):
            filtered_symbols.append(symbol)

    return filtered_symbols


def get_dates(
    init_offset=None,
    date_window=None,
    init_unit="days",
    date_window_unit="days",
):
    """
    Calculates dates for earnings data retrieval based on user input.

    Args:
        init_offset (int, optional): The desired offset from today.
                                      A positive value adds, negative subtracts.
                                      Defaults to None.
        date_window (int, optional): The desired window size between 'from_date' and 'to_date'.
                                      Defaults to None (same unit as init_offset).
        init_unit (str, optional): Unit for 'init_offset' (either "days", "weeks", or "quarters).
                                      Defaults to "days".
        date_window_unit (str, optional): Unit for 'date_window' (either "days", "weeks", or "quarters).
                                            Defaults to "days" (same unit as init_offset).

    Returns:
        tuple: A tuple containing two strings representing the 'from_date'
               and 'to_date' in YYYY-MM-DD format.

    Raises:
        ValueError: If 'init_unit' or 'date_window_unit' are not "days", "weeks", or "quarters
    """

    valid_units = ("days", "weeks", "quarters")
    if init_unit not in valid_units or date_window_unit not in valid_units:
        raise ValueError(
            "init_unit and date_window_unit must be either 'days' or 'weeks', or 'quarters'"
        )

    today = datetime.today()

    if init_offset is not None:
        if init_unit == "days":
            offset_delta = timedelta(days=init_offset)
        elif init_unit == "weeks":
            offset_delta = timedelta(weeks=init_offset)
        elif init_unit == "quarters":
            offset_delta = relativedelta(months=init_offset * 3)

        from_date_dt = today + offset_delta
        from_date = from_date_dt.strftime("%Y-%m-%d")

        if date_window is not None:
            if date_window_unit == "days":
                window_delta = timedelta(days=date_window)
            elif date_window_unit == "weeks":
                window_delta = timedelta(weeks=date_window)
            elif date_window_unit == "quarters":
                window_delta = relativedelta(months=date_window * 3)
        else:
            window_delta = timedelta(days=5)

        to_date_dt = from_date_dt + window_delta
        to_date = to_date_dt.strftime("%Y-%m-%d")

    return from_date, to_date


key_mapping = {
    "c": "Close",
    "h": "High",
    "l": "Low",
    "n": "Volume",
    "o": "Open",
    "t": "Datetime",
    "v": "Volume",
    "vw": "Volume Weighted Average Price",
}


def rename_keys(row):
    return {key_mapping.get(key, key): value for key, value in row.items()}


# symbols = get_upcoming_earnings("api-key", "05-21-24", "05-26-24")
symbols = ["EIM", "AAPL", "VINO"]

# remapped_data = [{key_mapping[key]: value for key, value in entry.items()} for entry in data]

from_date_history, to_date_history = get_dates(
    init_offset=-4, date_window=3, init_unit="quarters", date_window_unit="quarters"
)

url_parts = (
    "https://data.alpaca.markets/v2/stocks/bars",
    f"&timeframe=1Day&start={from_date_history}&end={to_date_history}&limit=10000&adjustment=raw&feed=sip&sort=asc",
)

normalized_dfs = []
data = []
for symbol in symbols:
    symbol_data = fetch_data(url_parts, symbol)
    data.append(pd.DataFrame(symbol_data))


for df, symbol in zip(data, symbols):
    normalized_df = pd.json_normalize(df[symbol])

    # Remap the column names
    normalized_df = normalized_df.rename(columns=key_mapping)

    # Insert the 'Symbol' column as the first column
    normalized_df.insert(0, "Symbol", symbol)

    normalized_dfs.append(normalized_df)

final_df = pd.concat(normalized_dfs, ignore_index=True)

print(final_df)

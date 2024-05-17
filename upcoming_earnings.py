import asyncio
import configparser
import json
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import aiohttp
import fmpsdk
from tqdm.asyncio import tqdm

import pandas as pd

config = configparser.ConfigParser()
config.read("api-keys.ini")


async def fetch_data(session, url_parts, symbol, progress_bar=None):
    base_url, rest_of_link = url_parts
    url = f"{base_url}?symbols={symbol}{rest_of_link}"
    async with session.get(url) as response:
        data = await response.json()
        if progress_bar:
            progress_bar.update(1)
        try:
            return data["bars"]
        except KeyError:
            return None


async def fetch_and_process(url_parts, symbols, headers, max_concurrent_tasks=5):
    chunks = []
    total_symbols = len(symbols)
    # Constants
    max_requests_per_minute = 250
    max_requests_per_second = max_requests_per_minute / 60

    # Adjust the sleep duration
    sleep_duration = 1 / (max_requests_per_second * max_concurrent_tasks)

    # Create the async progress bar
    pbar = tqdm(total=total_symbols, desc="Fetching and Processing Data")

    # Semaphore to limit concurrent tasks
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async with aiohttp.ClientSession(headers=headers) as session:

        async def limited_fetch_data(symbol):
            async with semaphore:
                await asyncio.sleep(1)
                chunk = await fetch_data(session, url_parts, symbol, pbar)
                return chunk

        tasks = [limited_fetch_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)

        for chunk in results:
            if chunk:
                chunks.append(pd.DataFrame.from_records(chunk))

    pbar.close()
    # Concatenate all chunks into a single DataFrame
    df = pd.concat(chunks, ignore_index=True)

    return chunks


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


def get_upcoming_earnings(api_key, from_date, to_date):
    earnings_data = fmpsdk.earning_calendar(
        apikey=api_key, from_date=from_date, to_date=to_date
    )

    filtered_symbols = []
    for earning in earnings_data:
        symbol = earning.get("symbol")
        # Filter if symbol exists, is a string, and doesn't end with country code extension
        if symbol and not re.search(r"\.[A-Z]*$", symbol):
            filtered_symbols.append(symbol)

    return filtered_symbols


async def main():
    fmp_api_key = config["API-KEYS"]["fmp-api-key"]
    apca_key_id = config["API-KEYS"]["apca-key-id"]
    apca_api_secret_key = config["API-KEYS"]["apca-api-secret-key"]

    from_date, to_date = get_dates(
        init_offset=3, date_window=5, date_window_unit="days", init_unit="days"
    )
    upcoming_earnings_symbols = get_upcoming_earnings(fmp_api_key, from_date, to_date)

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": apca_key_id,
        "APCA-API-SECRET-KEY": apca_api_secret_key,
    }

    from_date_history, to_date_history = get_dates(
        init_offset=-4, date_window=3, init_unit="quarters", date_window_unit="quarters"
    )

    url_parts = (
        "https://data.alpaca.markets/v2/stocks/bars",
        f"&timeframe=1Day&start={from_date_history}&end={to_date_history}&limit=10000&adjustment=raw&feed=sip&sort=asc",
    )

    chunks = await fetch_and_process(url_parts, upcoming_earnings_symbols, headers)

    for df in chunks:
        with open("output.json", "a") as outfile:
            # Convert each dataframe to a list of dictionaries
            df_list = df.to_dict(orient="records")

            # Append the list of dictionaries to the JSON file
            json.dump(df_list, outfile, indent=4)


if __name__ == "__main__":
    asyncio.run(main())

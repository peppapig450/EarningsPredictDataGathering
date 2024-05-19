import asyncio
import json
import re

import aiohttp
import fmpsdk
import pandas as pd
from tqdm.asyncio import tqdm

from config import apca_api_secret_key, apca_key_id, fmp_api_key


def normalize_and_rename(data, symbol):
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

    df = pd.DataFrame(data)
    normalized_df = pd.json_normalize(df[symbol])

    # Remap the column names
    normalized_df = normalized_df.rename(columns=key_mapping)

    # Insert the 'Symbol' column as the first column
    normalized_df.insert(0, "Symbol", symbol)

    return normalized_df


async def fetch_data(session, url_parts, symbol, progress_bar=None):
    base_url, rest_of_link = url_parts
    url = f"{base_url}?symbols={symbol}{rest_of_link}"
    async with session.get(url) as response:
        data = await response.json()
        if progress_bar:
            progress_bar.update(1)

        try:
            data = data["bars"]
            return normalize_and_rename(data, symbol)
        except KeyError:
            pass


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
            chunks.append(chunk)

    pbar.close()

    # Concatenate all chunks into a single DataFrame
    df = pd.concat(chunks, ignore_index=True)

    return df


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


# TODO: perfect async manipulation to ensure no too many request timeouts
async def main():
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

    data = await fetch_and_process(url_parts, upcoming_earnings_symbols, headers)
    data.to_csv("output.csv", index=False)
    symbol_data_dict = {
        symbol: group.drop(columns="Symbol").to_dict(orient="records")
        for symbol, group in data.groupby("Symbol")
    }
    with open("output.json", "w") as f:
        json.dump(symbol_data_dict, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())

import requests

url = "https://data.alpaca.markets/v2/stocks/bars?symbols=VINO&timeframe=1Day&start=2023-05-16&end=2024-02-16&limit=10000&adjustment=raw&feed=sip&sort=asc"

headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "AKNO0LZR9NJTASEB6IWZ",
    "APCA-API-SECRET-KEY": "bpvyP8Ci72D2CYGSnW59YachILcLL3lhdtX3emlw",
}

response = requests.get(url, headers=headers, timeout=30)
print(response.json())

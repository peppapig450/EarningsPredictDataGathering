from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass

url = "https://paper-api.alpaca.markets/v2/assets?attributes="

api_keys = ("AKNO0LZR9NJTASEB6IWZ", "bpvyP8Ci72D2CYGSnW59YachILcLL3lhdtX3emlw")

trading_client = TradingClient(
    "AKNO0LZR9NJTASEB6IWZ", "bpvyP8Ci72D2CYGSnW59YachILcLL3lhdtX3emlw"
)
# search for US equities
# search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
account = trading_client.get_account()

# assets = trading_client.get_all_assets(search_params)
print(account)

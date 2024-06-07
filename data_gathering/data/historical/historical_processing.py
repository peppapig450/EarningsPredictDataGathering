import pandas as pd
from collections import defaultdict
from data_gathering.models.mappings import historical_data_mapping


class HistoricalDataProcessing:
    # queue later
    def __init__(self) -> None:
        self.data_dict = defaultdict(list)

    def rename_columns(self, response_data):
        for batch in response_data:
            for symbol, data in batch.items():
                for i, bar in enumerate(data):
                    renamed_bar = {
                        historical_data_mapping[key]: val
                        for key, val in bar.items()
                        if key in historical_data_mapping
                    }
                    renamed_bar["symbol"] = symbol
                    data[i] = renamed_bar

                self.data_dict[symbol] = data

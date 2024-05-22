from data_gathering.utils.output import OutputUtils
import pandas as pd
from typing import Dict


class HistoricalDataOutputUtils(OutputUtils):
    @staticmethod
    def combine_symbol_dataframes(
        historical_data_by_symbols: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Combines historical data DataFrames into a single DataFrame.

        Args:
            historical_data_by_symbols (Dict[str, pd.DataFrame]): A dictionary mapping symbols to DataFrames
                containing historical data.

        Returns:
            pd.DataFrame: A DataFrame containing the combined historical data, with a multi-index
                consisting of 'Symbol' and 'Datetime'.

        Example:
            historical_data_by_symbols = {
                'AAPL': historical_data_for_aapl_df,
                'GOOG': historical_data_for_goog_df
            }
            combined_df = HistoricalDataOutputUtils.combine_symbol_dataframes(historical_data_by_symbols)
        """
        combined_historical_data_df = pd.concat(
            historical_data_by_symbols.values(),
            keys=historical_data_by_symbols.keys(),
            names=["Symbol", "Datetime"],
        )

        return combined_historical_data_df

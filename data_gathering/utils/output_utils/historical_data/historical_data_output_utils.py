import os
from data_gathering.utils.output import OutputUtils
import pandas as pd
from typing import Dict
import json


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

    # TODO: maybe rewrite so it works for any dataframe
    @staticmethod
    def output_combined_symbol_df_to_json(combined_df: pd.DataFrame, output_filename):
        # Define a vectorized function within the scope of the current function to process grouped DataFrame
        # and convert it into a nested dictionary (fastest way by 8 milliseconds)
        def g(group):
            return group.groupby("Datetime")["data"].apply(list).to_dict()

        # Creating output file path
        output_filepath = os.path.join("output", output_filename)

        # Selecting the columns of interest
        selected_columns = [
            "Close",
            "High",
            "Low",
            "Number of Trades",
            "Open",
            "Volume",
            "VWAP",
        ]

        # Creating a new column 'data' with the relevant data
        combined_df["data"] = combined_df[selected_columns].to_dict(orient="records")

        # Grouping by 'Symbol' and 'Datetime' and creating nested dictionary directly
        nested_dict = combined_df.groupby("Symbol").apply(g).to_dict()

        # Converting the final result to JSON with the ISO date format
        return pd.Series(nested_dict).to_json(output_filepath, date_format="iso")

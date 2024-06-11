from collections import defaultdict
from itertools import chain
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

from data_gathering.models.mappings import historical_data_mapping


class HistoricalDataProcessing:
    """
    A class used to process historical data for financial instruments.

    Attributes
    ----------
    data_dict : defaultdict
        A dictionary to hold the processed data.
    """

    # queue later
    def __init__(self) -> None:
        """Initialize the HistoricalDataProcessing class with an empty data dictionary."""
        self.data_dict: defaultdict = defaultdict(list)

    # TODO: maybe make response_data an instance variable, (get it from the queue)

    # XXX: find a way to rewrite this im not fw it
    def rename_columns(self, response_data: list[dict[str, Any]]) -> None:
        """
        Rename the columns in the response data according to a predefined mapping.

        Parameters
        ----------
        response_data : List[Dict[str, Any]]
            The data received from an external source, which needs to be processed.
        """
        for batch in response_data:
            for symbol, data in batch.items():
                for i, daily_bar in enumerate(data):
                    renamed_bar = {
                        historical_data_mapping[key]: val
                        for key, val in daily_bar.items()
                        if key in historical_data_mapping
                    }
                    renamed_bar["symbol"] = symbol
                    data[i] = renamed_bar

                self.data_dict[symbol] = data

    def create_dataframe(self, renamed_data) -> pd.DataFrame:
        """
        Rename the columns in the response data according to a predefined mapping.

        Parameters
        ----------
        response_data : List[Dict[str, Any]]
            The data received from an external source, which needs to be processed.
        """
        flatted_data_list = list(chain.from_iterable(renamed_data.values()))

        df = pd.DataFrame(flatted_data_list)

        if set(["symbol", "timestamp"]).issubset(df.columns):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index(["symbol", "timestamp"], inplace=True)

        return df

    @staticmethod
    def write_to_parquet(
        dataframe: pd.DataFrame, filename: str = "historical_data.parquet"
    ) -> None:
        """
        Write the DataFrame to a Parquet file.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The DataFrame to be written to a Parquet file.
        filename : str, optional
            The name of the file to write to (default is "historical_data.parquet").
        """
        dataframe.to_parquet(filename)

    @staticmethod
    def read_parquet_table(
        filename: str = "historical_data.parquet",
    ):
        table = pq.read_table(filename, use_pandas_metadata=True)
        return table

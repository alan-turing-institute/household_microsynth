"""Inside this file contains a class with a method that may be customised to override the default output behaviour of
household_microsynth. For example, you may use this if you wish to send the output to some an alternative destination
such as a database, write in an alternative format, or both.

The method must take a DataFrame which is the object type household_microsynth builds.
The default behaviour is to write this object into the local ./data directory as a .csv file.
"""
from pathlib import Path
import os


class OutputHelper:
    OUTPUT_DIR = "./data"

    @staticmethod
    def __custom_endpoint(dataframe):
        """WRITE IMPLEMENTATION HERE"""
        raise NotImplementedError  # Remove this line if using the custom endpoint.

    def __default_endpoint(self, dataframe):
        output_path = Path() / self.OUTPUT_DIR / dataframe.name
        if not os.path.isdir("./data"):
            os.mkdir("./data")
        print("Writing synthetic population to", str(output_path))
        if dataframe.name[:2] == "hh":
            dataframe.to_csv(output_path, index_label="HID")
        elif dataframe.name[:3] == "hrp":
            dataframe.to_csv(output_path)

    def send(self, pandas_df):
        try:
            self.__custom_endpoint(pandas_df)
        except NotImplementedError:
            self.__default_endpoint(pandas_df)


Output = OutputHelper()



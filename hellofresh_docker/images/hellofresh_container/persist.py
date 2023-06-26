import logging

from images.hellofresh_container.utility import spark_utility

logger = logging.getLogger("persist")


class Persist:
    def __init__(self, spark):
        self.spark = spark

    def persist_csv_records(self, df, file):
        # write into scv file
        return spark_utility.write_csv_file(df, file)

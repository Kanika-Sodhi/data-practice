import os

import findspark
from images.hellofresh_container.utility import spark_utility
import logging

findspark.init()

logger = logging.getLogger("ingest")


class Ingest:
    def __init__(self, spark):
        self.spark = spark

    def schema_validation(self, recipes_folder, raw_data, template_path, recipe_temp_file_name):
        try:
            logger.info("schema validation started")
            # Check if each file exists in the folder
            if len(os.listdir(recipes_folder)) == 0:
                raise Exception("Directory is empty")
            else:
                logger.info("Directory is not empty")

            # reading data from raw file
            json_data = spark_utility.reading_json_file(self.spark, recipes_folder + raw_data)
            if json_data.count() == 0:
                raise Exception("File is empty")
            # reading data from csv template file
            reading_template = spark_utility.reading_csv_file(self.spark, template_path + recipe_temp_file_name, True)
            # creating the column list
            json_col_type = json_data.columns
            csv_col_type = reading_template.columns
            # checking if json schema and template schema matching for ensuring schema match
            if len(json_col_type) == 0 | len(csv_col_type) == 0:
                logger.info("list is empty")
                raise ValueError('empty list')
            if csv_col_type == json_col_type:
                logger.info("template and json schema matching")
                return json_data
            else:
                raise ValueError("Template and JSON List fields are not Equal")

        except FileNotFoundError as e:
            logger.error("File not found:", str(e))

        except ValueError as e:
            logger.error("Invalid value:", str(e))

        except Exception as e:
            logger.error("Error:", str(e))

    def ingest_data(self, validate_df, write_path):
        try:
            if validate_df.count() > 0:
                validate_df.write.mode("overwrite").parquet(write_path)
                logger.info("data ingested into ingest folder")
            else:
                raise Exception("Dataframe id Empty")
        except Exception as e:
            logger.error("Error:", str(e))

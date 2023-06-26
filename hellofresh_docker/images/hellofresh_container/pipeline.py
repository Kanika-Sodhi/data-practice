import logging
from pyspark.sql import SparkSession
from ingest import Ingest
import transform
from parameter_file import filter_ingredient, persist_path, template_path, recipes_raw_data, recipe_temp_file_name, \
    recipes_folder, ingest_write_path, tablename, ingest_read_path
from images.hellofresh_container import persist
from images.hellofresh_container.recipe_difficulty_insights import recipe_difficulties_wise_insights
import findspark

findspark.init()

logger = logging.getLogger("pipeline")


class Pipeline:

    def __init__(self, name):
        # creating spark session
        self.spark = SparkSession \
            .builder \
            .appName(name) \
            .getOrCreate()

    def run_pipeline(self):
        try:
            # initialization of persist class
            persist_process = persist.Persist(self.spark)
            logger.info('run_pipeline method started')
            # calling all the process of extraction
            ingest_process = Ingest(self.spark)
            # validating schema and file
            validate_df = ingest_process.schema_validation(recipes_folder, recipes_raw_data, template_path,
                                                           recipe_temp_file_name)
            logger.info('schema validation done')
            # ingesting data in ingest folder
            ingest_process.ingest_data(validate_df, ingest_write_path)
            logger.info('ingest done')
            # creating transform data object initialization
            transform_process = transform.Transform(self.spark)
            transformed_df = transform_process.parse_columns(tablename, ingest_read_path)
            logger.info('parse done')
            transformed_with_dq = transform_process.data_quality_checks(transformed_df)
            logger.info('data quality checks done')
            # transformed_with_incremental = transform_process.incremental_load(transformed_with_dq)
            # logger.info('incremental done')
            # transformed_with_incremental.show()
            recipe_difficulties = recipe_difficulties_wise_insights(transformed_with_dq, filter_ingredient)
            logger.info('recipe difficulties insights done')
            # recipe_difficulties.show()

            persist_process.persist_csv_records(recipe_difficulties, persist_path)
            logging.info('run_pipeline method ended')
        except BaseException as error:
            logger.error(f"FoundError {error}", exc_info=True)

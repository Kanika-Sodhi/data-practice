import logging

import findspark
from pyspark.sql.types import IntegerType
import pyspark.sql.functions as f
from images.hellofresh_container.parameter_file import template_path, transformed_path, \
    incremental_path, recipe_temp_file_name, recipe_schema
from pyspark.sql.functions import md5, concat_ws
from images.hellofresh_container.utility import spark_utility, common_utility

findspark.init()

logger = logging.getLogger("transform")


class Transform:
    def __init__(self, spark):
        self.spark = spark

    def parse_columns(self, tablename, ingest_read_path):
        try:
            logger.info("parsing of column started")
            # reading ingested data in the parquet format
            ingested_data = spark_utility.reading_parquet_file(self.spark, ingest_read_path)
            logger.debug("ingest data successfully read")
            # reading data from csv template file
            reading_template = spark_utility.reading_csv_file(self.spark, template_path + recipe_schema,
                                                              header=True)
            logger.debug("template data successfully read")
            # checking table name must not be null
            if tablename == '':
                raise Exception("table name is empty")
            # parsing data according to the defined fields
            parse_df = common_utility.cast_columns(ingested_data, reading_template, tablename)
            logger.info("parsing of the column done")
            return parse_df
        except Exception as e:
            logger.error("Error:", str(e))

    def data_quality_checks(self, json_data):
        try:
            logger.info("Quality data started")
            # dropping rows having null values
            json_data_without_null = json_data.dropDuplicates()
            logger.debug("dropping rows duplicate records values")

            # Converting function to UDF
            get_minutes_UDF = f.udf(lambda z: common_utility.get_minutes(z), IntegerType())

            format_json_data = json_data_without_null.select(json_data.ingredients,
                                                             json_data.datePublished, json_data.description,
                                                             json_data.name,
                                                             json_data.image, json_data.recipeYield, json_data.url,
                                                             get_minutes_UDF(f.col("cookTime")).alias("cookTime"),
                                                             get_minutes_UDF(f.col("prepTime")).alias("prepTime")) \
                .withColumn("activeRecords", f.lit(0))
            logger.debug("reads ingest data without null values")

            # casting of cooktime and preparetime to integer
            format_json_data = format_json_data \
                .withColumn("cookTime_mins", format_json_data.cookTime.cast(IntegerType())) \
                .withColumn("prepTime_mins", format_json_data.prepTime.cast(IntegerType()))

            format_json_data = format_json_data.select(format_json_data.ingredients, format_json_data.datePublished,
                                                       format_json_data.description,
                                                       format_json_data.name, format_json_data.image,
                                                       format_json_data.recipeYield, format_json_data.url,
                                                       format_json_data.cookTime_mins,
                                                       format_json_data.prepTime_mins, format_json_data.activeRecords)

            logger.info("Quality data passed")
            return format_json_data
        except Exception as e:
            logger.error(f"FoundError {e}")

    def incremental_load(self, transformed_with_dq):
        logger.info("checking changed and new data started")
        # reading transformed data
        recipe_dim = spark_utility.reading_csv_file(self.spark, transformed_path + recipe_temp_file_name, True)

        # selecting required columns for md5 from dim table
        recipe_dim_new = recipe_dim.select(recipe_dim.ingredients_dim,
                                           recipe_dim.description_dim,
                                           recipe_dim.image_dim,
                                           recipe_dim.cookTime_mins_dim, recipe_dim.prepTime_mins_dim)

        logger.debug("creating md5 for selected columns from recipe_dim")

        # selecting required columns for md5 from transformed table
        transformed_with_dq_new = transformed_with_dq.select(transformed_with_dq.ingredients,
                                                             transformed_with_dq.description,
                                                             transformed_with_dq.image,
                                                             transformed_with_dq.cookTime_mins,
                                                             transformed_with_dq.prepTime_mins)
        logger.debug("creating md5 for selected columns from dq passed data")

        # Adding md5 column with selected list for recipe_dim_new
        recipe_dim = recipe_dim.withColumn("md5_dim", md5(concat_ws("||", *recipe_dim_new)))
        # Adding md5 column with selected list for transformed_with_dq_new
        transformed_with_dq = transformed_with_dq.withColumn("md5",
                                                             md5(concat_ws("||", *transformed_with_dq_new)))
        logger.debug("added md5 column in original data")

        # joining both table to check new records
        cond_new = [recipe_dim.name_dim == transformed_with_dq.name,
                    recipe_dim.datePublished_dim == transformed_with_dq.datePublished]
        new_recipe_insert = transformed_with_dq.join(recipe_dim, cond_new, "left_outer").where(
            recipe_dim.md5_dim.isNull()).select(transformed_with_dq['*'])

        logger.debug("new records fetched")

        # joining both table to check updated records
        cond_update = [recipe_dim.name_dim == transformed_with_dq.name,
                       recipe_dim.datePublished_dim == transformed_with_dq.datePublished]
        recipe_update_new = transformed_with_dq.join(recipe_dim, cond_update, "inner").where(
            recipe_dim.md5_dim != transformed_with_dq.md5).select(transformed_with_dq['*'])

        logger.debug("updated records fetched")

        # joining both table to check expired records
        cond_update = [recipe_dim.name_dim == transformed_with_dq.name,
                       recipe_dim.datePublished_dim == transformed_with_dq.datePublished]
        recipe_expired = transformed_with_dq.join(recipe_dim, cond_update, "inner").where(
            recipe_dim.md5_dim != transformed_with_dq.md5).select(recipe_dim['*'])

        recipe_expired = recipe_expired.withColumn("activeRecords", f.lit(1))
        logger.debug("expired records fetched")

        new_data_set = new_recipe_insert.union(recipe_update_new).union(recipe_expired)
        logger.debug("combined new,updated and expired records")

        n = 2  # number of repartitions, try 2 to test
        new_data_set = new_data_set.repartition(n)

        new_data_set.write.mode("overwrite").parquet(incremental_path)
        # inserting data in persist folder
        logger.info("incremental load ends")

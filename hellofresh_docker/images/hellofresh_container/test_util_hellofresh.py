import os
from unittest import TestCase
from unittest.mock import MagicMock

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, BooleanType
from images.hellofresh_container import transform, ingest
from images.hellofresh_container.parameter_file import template_path, recipe_temp_file_name
from images.hellofresh_container.recipe_difficulty_insights import recipe_difficulties_wise_insights
from images.hellofresh_container.utility import spark_utility, common_utility


class UtilsTestCase(TestCase):
    spark = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.spark = SparkSession.builder \
            .appName("HelloFreshSparkTest") \
            .getOrCreate()

    def test_schema_validation(self):
        # test recipe folder
        recipes_folder = '../../data/test_data/'
        # reading data from raw file
        test_recipes_raw_data = 'recipes-000.json'
        # positive scenario
        ingest_process = ingest.Ingest(self.spark)
        result = ingest_process.schema_validation(recipes_folder,
                                                  test_recipes_raw_data, template_path, recipe_temp_file_name)
        self.assertEqual(result.count(), 484)

        # test recipe folder
        recipes_folder = '../../data/checking_testcase/'
        # reading data from raw file
        test_recipes_raw_data = 'recipes-011.json'
        # directory is empty
        with pytest.raises(Exception, match=r"Directory is empty"):
            ingest_process.schema_validation(recipes_folder,
                                             test_recipes_raw_data, template_path, recipe_temp_file_name)

        # test recipe folder
        recipes_folder = '../../data/test_data/'
        # reading data from raw file
        test_recipes_raw_data = 'recipes-090.json'
        # columns are not matching
        with pytest.raises(Exception, match=r"Template and JSON List fields are not Equal"):
            ingest_process.schema_validation(recipes_folder,
                                             test_recipes_raw_data, template_path, recipe_temp_file_name)
        return result

    def test_ingest_data(self):
        input_json_data = self.spark.createDataFrame(
            [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              "PT20M", "PT5M"),
             ("Water", "2023-04-28", "This is a recipe for water.", "Water Recipe",
              "water.png", "1 serving", "https://www.waterrecipe.com",
              "PT5M", "PT2M"),
             ("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              "PT20M", "PT5M")], ["ingredients", "datePublished", "description",
                                  "name", "image", "recipeYield", "url",
                                  "cookTime", "prepTime"])
        # Call the ingest_data function with the valid DataFrame
        write_path = '../../data/test_data'
        ingest_process = ingest.Ingest(self.spark)
        result = ingest_process.ingest_data(input_json_data, write_path)

        # Assert that the result is the same as the input DataFrame
        self.assertIsNone(result)
        # Check if the folder is not empty
        assert len(os.listdir(write_path)) > 0, "The folder is empty"

        # Create an empty DataFrame
        input_json_data = input_json_data.filter("1=0")
        # Call the ingest_data function with the empty DataFrame
        write_path = '../../data/test_data'
        with pytest.raises(Exception, match=r"Dataframe id Empty"):
            ingest_process.ingest_data(input_json_data, write_path)

    def test_cast_columns(self):
        data = [
            (1, 'a', 1.1, True),
            (2, 'b', 2.2, False),
            (3, 'c', 3.3, True),
            (4, 'd', 4.4, True)
        ]

        schema = StructType([
            StructField("col1", IntegerType(), True),
            StructField("col2", StringType(), True),
            StructField("col3", FloatType(), True),
            StructField("col4", BooleanType(), True)
        ])

        # Create a data frame
        df = self.spark.createDataFrame(data, schema=schema)

        # Define the dictionary of expected data types
        merged_data = [
            ('col1', 'int', 'recipe'),
            ('col2', 'str', 'recipe'),
            ('col3', 'float', 'recipe'),
            ('col4', 'bool', 'recipe')
        ]

        merged_schema = StructType([
            StructField("fields", StringType()),
            StructField("dtype", StringType()),
            StructField("tablename", StringType())
        ])

        # Create a data frame
        merged_df = self.spark.createDataFrame(merged_data, schema=merged_schema)
        # parsing data according to the defined fields
        parse_df = common_utility.cast_columns(df, merged_df, 'recipe')
        self.assertIsNotNone(df)
        self.assertIsNotNone(merged_df)
        self.assertIsNotNone(parse_df)
        # check if all expected columns are present in the output
        self.assertListEqual(df.columns, parse_df.columns)
        # check if all rows are present in the output
        self.assertEqual(df.count(), parse_df.count())

    def test_parse_columns(self):
        # Call the ingest_data function with the empty DataFrame
        transform_process = transform.Transform(self.spark)
        # test recipe folder
        recipes_folder = '../../data/test_data/'
        # reading data from raw file
        test_recipes_raw_data = 'recipes-000.json'
        tablename = 'recipes'
        result = transform_process.parse_columns(tablename, recipes_folder + test_recipes_raw_data)
        self.assertIsNotNone(result)
        self.assertEqual(result.count(), 484)

        tablename = ''
        with pytest.raises(Exception, match=r"table name is empty"):
            transform_process.parse_columns(tablename, recipes_folder + test_recipes_raw_data)

    def test_data_quality_checks(self):
        input_json_data = self.spark.createDataFrame(
            [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              "PT20M", "PT5M"),
             ("Water", "2023-04-28", "This is a recipe for water.", "Water Recipe",
              "water.png", "1 serving", "https://www.waterrecipe.com",
              "PT5M", "PT2M"),
             ("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              "PT20M", "PT5M")], ["ingredients", "datePublished", "description",
                                  "name", "image", "recipeYield", "url",
                                  "cookTime", "prepTime"])
        expected_result = self.spark.createDataFrame(
            [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              20, 5, 0),
             ("Water", "2023-04-28", "This is a recipe for water.", "Water Recipe",
              "water.png", "1 serving", "https://www.waterrecipe.com",
              5, 2, 0)], ["ingredients", "datePublished", "description",
                          "name", "image", "recipeYield", "url",
                          "cookTime_mins", "prepTime_mins", "activeRecords"
                          ])
        # Act
        transform_process = transform.Transform(self.spark)
        result = transform_process.data_quality_checks(input_json_data)
        # result.select()

        # Assert
        assert result is not None
        self.assertListEqual(result.columns, expected_result.columns)
        assert result.count() == expected_result.count()
        assert result.collect() == expected_result.collect()

    def test_recipe_difficulties_wise_insights(self):
        # Empty dataframe test
        empty_df = self.spark.createDataFrame([],
                                              schema="ingredients INT,datePublished date, name STRING, description "
                                                     "STRING, prepTime_mins INT, image STRING, "
                                                     "recipeYield STRING,url STRING,  cookTime_mins INT,activeRecords "
                                                     "INT")
        with pytest.raises(Exception, match=r"Dataframe is empty"):
            recipe_difficulties_wise_insights(empty_df, "onion")

        # Empty ingredient filter test
        df_empty = self.spark.createDataFrame(
            [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              20, 5, 0)],
            schema="ingredients STRING,datePublished STRING, description STRING, name STRING, "
                   "image STRING, recipeYield STRING,url STRING,  cookTime_mins INT,prepTime_mins INT,activeRecords INT")

        with pytest.raises(Exception, match=r"filter ingredient is empty"):
            recipe_difficulties_wise_insights(df_empty, '')

        transformed_with_dq = self.spark.createDataFrame(
            [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
              "salt.png", "2 servings", "https://www.saltrecipe.com",
              20, 5, 0),
             ("Water", "2023-04-28", "This is a recipe for water.", "Water Recipe",
              "water.png", "1 serving", "https://www.waterrecipe.com",
              5, 2, 0),
             ("Water", "2023-04-28", "This is a recipe for water and salt.", "Water & salt Recipe",
              "water&salt.png", "1 serving", "https://www.waterrecipe.com",
              75, 2, 0)
             ], ["ingredients", "datePublished", "description",
                 "name", "image", "recipeYield", "url",
                 "cookTime_mins", "prepTime_mins", "activeRecords"
                 ])
        filter_ingredient = 'water'
        recipe_difficulties_df = recipe_difficulties_wise_insights(transformed_with_dq, filter_ingredient)

        expected_df = self.spark.createDataFrame([('EASY', 7.0), ('HARD', 77.0)],
                                                 schema="difficulty STRING, avg_total_cooking_time DOUBLE")

        assert recipe_difficulties_df.collect() == expected_df.collect()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.spark.stop()

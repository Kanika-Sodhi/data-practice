import os

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, FloatType, BooleanType

# Create a SparkSession
from images.hellofresh_container import transform, ingest
from images.hellofresh_container.parameter_file import recipes_raw_data, template_path, recipe_temp_file_name
from images.hellofresh_container.recipe_difficulty_insights import recipe_difficulties_wise_insights
from images.hellofresh_container.utility import common_utility, spark_utility

spark = SparkSession.builder.appName("DataTypeCheck").getOrCreate()

data = [
    (1, 'a', 1.1, True),
    (2, 'b', 2.2, False),
    (3, 'c', 3.3, True),
    (4, 'd', 4.4, True)
]

schema = StructType([
    StructField("col1", StringType(), True),
    StructField("col2", StringType(), True),
    StructField("col3", StringType(), True),
    StructField("col4", StringType(), True)
])

# Create a data frame
df = spark.createDataFrame(data, schema=schema)

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
'''merged_df = spark.createDataFrame(merged_data, schema=merged_schema)
parse_df = common_utility.cast_columns(df, merged_df, 'recipe')
parse_df.printSchema()
df.show()
merged_df.show()'''

input_json_data = spark.createDataFrame(
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
expected_result = spark.createDataFrame(
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
transform_process = transform.Transform(spark)
result = transform_process.data_quality_checks(input_json_data)

transformed_with_dq = spark.createDataFrame(
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

recipe_difficulties = recipe_difficulties_wise_insights(transformed_with_dq, filter_ingredient)

# Empty ingredient filter test
df_empty = spark.createDataFrame(
    [("Salt", "2023-04-28", "This is a recipe for salt.", "Salt Recipe",
      "salt.png", "2 servings", "https://www.saltrecipe.com",
      20, 5, 0)],
    schema="ingredients STRING,datePublished STRING, description STRING, name STRING, "
           "image STRING, recipeYield STRING,url STRING,  cookTime_mins INT,prepTime_mins INT,activeRecords INT")

# df_rec_empty = recipe_difficulties_wise_insights(df_empty, '')

transformed_with_dq = spark.createDataFrame(
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
expected_df = spark.createDataFrame([('EASY', 7.0), ('HARD', 77.0)],
                                    schema="difficulty STRING, avg_total_cooking_time DOUBLE")

'''print(recipe_difficulties_df.collect())
print(expected_df.collect())
if expected_df.collect() == recipe_difficulties_df.collect():
    print("yes")'''


class ABC:
    def __init__(self, spark):
        self.spark = spark

    def abcde(self):
        # reading data from raw file
        test_recipes_raw_data = ['../../data/test_data/recipes-000.json']
        # Set the folder path where JSON files are located
        ingest_process = ingest.Ingest(spark)
        result = ingest_process.schema_validation(self, test_recipes_raw_data, template_path + recipe_temp_file_name)
        result.show()


spark = SparkSession \
    .builder \
    .appName("name") \
    .getOrCreate()
a = ABC(spark)

df3 = spark.read.json("../../data/input/*.json")
print(df3.count())




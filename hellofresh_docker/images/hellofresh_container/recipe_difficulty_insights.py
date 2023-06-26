import logging

from pyspark.sql.functions import *
import pyspark.sql.functions as f

logger = logging.getLogger("difficulties_insights")


def recipe_difficulties_wise_insights(transformed_with_dq, filter_ingredient):
    try:
        logger.info("recipe_difficulties_wise_insights started")

        # checking if dataframe is empty or not
        if transformed_with_dq.count() == 0:
            raise Exception("Dataframe is empty")
        if filter_ingredient is None or filter_ingredient == '':
            raise Exception("filter ingredient is empty")

        # checking filter record
        ingredient = transformed_with_dq.where(f.lower("ingredients")
                                               .like(f"%{filter_ingredient}%"))

        logger.debug("filtered ingredient")

        # adding total cooking time column
        ingredient = ingredient.withColumn("total_cook_time", ingredient.prepTime_mins
                                           + ingredient.cookTime_mins)
        logger.debug("total cooking time column added")

        # adding difficulty level column according to cooking time
        ingredient = ingredient.withColumn("difficulty",
                                           f.when(ingredient.total_cook_time > 60, "HARD")
                                           .when(ingredient.total_cook_time < 30, "EASY")
                                           .when((f.col("total_cook_time") >= 30)
                                                 & (f.col("total_cook_time") <= 60), "MEDIUM"))
        logger.debug("added difficulty level column according to cooking time")

        # aggregating according to difficulty level of cooking
        ingredient = ingredient.groupBy("difficulty").agg(
            round(avg("total_cook_time"), 2).alias("avg_total_cooking_time"))
        logger.debug("difficulties insights added with average time")

        return ingredient
    except Exception as e:
        logger.error("Error:", str(e))
